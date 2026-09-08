> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: `git status --porcelain` → 0 lines (repo untouched); both scripts exit 0; re-read the ask — all three stop-condition parts (disagreement count, verbatim check on all ten, local-recurrence column) are delivered. Full report below.

---

## Worker

- **Worker ID:** W08b (refill for lane 8), OPUS-CAPACITY-CAMPAIGN-20260908. Role: **independent adjudicator running W08's own falsification test against W08's own result.**
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system prompt states I am powered by "Opus 5", exact model ID `claude-opus-5`. I did not observe the served model and do not assert it as fact; the coordinator must extract the actual per-child runtime model from the transcript.
- **Start of run, `date -u`:** `Tue Sep  8 02:06:26 UTC 2026`
- **End of run, `date -u`:** `Tue Sep  8 02:10:40 UTC 2026`
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** — captured at start; identical at end (same container, no re-exec). Verbatim, with the long `no_proxy`/`NO_PROXY`/`GLOBAL_AGENT_NO_PROXY`/`npm_config_noproxy`/`JAVA_TOOL_OPTIONS` values elided as noted:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...                  [elided: proxy host list]
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...     [elided]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ...   [elided]
NO_PROXY=localhost,127.0.0.1,::1,...                  [elided]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...        [elided]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

- **Write isolation: COMPLIED.** All execution in `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/W08b/`. `git status --porcelain | wc -l` → `0`. No git write operation of any kind. No file written under `/home/user/Rare-cancers`.

### A material caveat on my independence, stated before the result

My dispatch's STEP 0 required me to read `reports/W08-disease-course-surveillance-question.md` **in full** before adjudicating. That file contains W08's complete included table, its ten quoted sentences, and its exclusion list. Instruction 2 then asked me to adjudicate "before looking at W08's included set in detail." **These two instructions are in direct conflict, and STEP 0 came first, so my adjudication is NOT blinded.** I worked forward from the abstracts (my own screen output, then reading each candidate's full abstract from the retrieved JSON) rather than backward from W08's list, and the one disagreement I found is an *addition* W08 missed — which is the direction anchoring bias makes *harder*, not easier, to find. But an unblinded re-adjudication is systematically biased toward agreement, and this confirmation must be discounted accordingly. A genuinely blinded second adjudication is still outstanding. I am reporting this rather than claiming an independence I did not have.

---

## Question

Does W08's patient-level metastasis-interval census survive **its own** stated falsification condition?

> *"If an independent adjudicator, applying the stated inclusion rule to the same 84 abstracts, produces an included set differing by more than one patient-event, or if any quoted sentence does not appear verbatim in its cited abstract, the table is wrong."*

Three sub-questions, all executable in this container: (1) is the frame still `total_count = 84`; (2) does an independent pass over the same 84 abstracts reproduce the included set within one event; (3) do all ten quoted sentences appear verbatim. Plus the second column W08 named but did not build: the **local recurrence** interval, separately anchored.

**Why it is open.** W08 wrote the falsification condition but could not run it against itself — that is what "independent" means. Its named successor had two halves; the full-text promotion needs routes this container does not have (and which `CLOSED-WORK.md` records as denied), the re-adjudication does not.

---

## Prior-work check

Commands run from `/home/user/Rare-cancers` (read-only):

```
cat research/autonomy/opus-capacity-campaign-20260908/COMMON-BRIEF.md
cat research/autonomy/opus-capacity-campaign-20260908/CLOSED-WORK.md
cat research/autonomy/opus-capacity-campaign-20260908/reports/W08-disease-course-surveillance-question.md
git status --porcelain | wc -l          # -> 0
```

What I confirmed I am **not** replaying:
- **AUT-065 / RT-SURVEILLANCE** and `research/modalities/emc-recurrence-timing.json`: I read neither file and pooled nothing with their cohort medians. My values are patient-level and separately anchored.
- **Closed gates in `CLOSED-WORK.md`**: conditional-recurrence, RT/IPD synthesis, trial-discoverability, the user-rejected ICD-O registry paper, methylation. None re-proposed. I read no registry file.
- **Denied routes**: I did **not** probe `eutils.ncbi.nlm.nih.gov` (recorded by W08 as `CONNECT tunnel failed, response 403`) and did not attempt any publisher full-text route recorded as 403. All retrieval went through the PubMed MCP server. The full-text half of W08's successor is therefore **not attempted here** and remains open.
- **W08 itself**: I re-derived the census rather than restating it, which is the point of the task.

---

## Method / inputs

- **Tooling:** PubMed MCP server (`mcp__PubMed__search_articles`, `mcp__PubMed__get_article_metadata`); Python 3.11 (`statistics`, `json`, `re`); GNU coreutils.
- **According to PubMed**, the frame is the query `extraskeletal myxoid chondrosarcoma AND (metastasis OR recurrence) AND case reports[Publication Type]`, sort=relevance, retrieved 2026-09-08.
- **Retrieval:** two `search_articles` pages (`retstart` 0 and 50) returned 50 + 34 = 84 PMIDs, 84 unique after `sort -u`. Five `get_article_metadata` calls (20/20/20/20/4). I independently reproduced W08's measured API behaviour note in the inverse: passing exactly 20 PMIDs returns exactly 20, and my screen's `frame - seen` set-difference confirmed the 24 not in the persisted files were exactly the 24 returned inline. Coverage 84/84, verified by set difference, not assumed.
- **Files, all outside the repository**, in `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/W08b/`: `frame.txt`, `frame_sorted.txt`, `c1.json`–`c3.json` (60 abstracts), `w08b_screen.py`, `w08b_verify.py`.
- **Two-stage extraction, deliberately separated** (as W08 did, so the two are comparable): a regex screen over the 60 persisted abstracts producing a raw candidate sentence pool, then hand adjudication over all 84 with the full abstract of every flagged candidate read in full before a verdict.

### Inclusion rules, stated before extraction

**Column A — first distant or regional metastasis** (W08's rule, transcribed and applied unchanged): EMC patient; explicit numeric elapsed interval; anchor = primary diagnosis or primary surgery; endpoint = first documented distant or regional (nodal) metastasis. Excluded: metastasis synchronous with or preceding the primary; intervals to death or to follow-up rather than to the event; approximate or bounded intervals (recorded separately as imprecise); non-EMC histology.

**Column B — first local recurrence** (mine, stated before I extracted it): EMC patient; explicit numeric elapsed interval; anchor = primary diagnosis or primary resection; endpoint = **first** documented local recurrence at the primary site or operative bed. Excluded: a recurrence anchored to an *earlier recurrence* rather than to the primary; an interval to death rather than to the recurrence; recurrence at a non-primary site (counted as regional/distant instead, never in both columns).

### Code

```python
#!/usr/bin/env python3
"""W08b independent re-adjudication screen.
Reads persisted PubMed metadata JSON, reports (a) frame coverage,
(b) every sentence containing an elapsed-time expression, so the
adjudicator sees the raw candidate pool without W08's row list.
Screen only. No inference, no scoring."""
import json, sys, re

NUMWORD = ("one two three four five six seven eight nine ten eleven twelve "
           "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty").split()
NUM = r"(?:\d+(?:[.,]\d+)?|" + "|".join(NUMWORD) + r")"
# an elapsed-time expression: N year/month/week (hyphen or space)
TIME = re.compile(rf"\b{NUM}[-\s]+(?:year|month|week|yr|mo)s?\b", re.I)
SENT = re.compile(r"[^.;]*(?:[.;]|$)")

def sentences(text):
    return [s.strip() for s in SENT.findall(text) if s.strip()]

def main(paths, frame_path="frame_sorted.txt"):
    frame = set(open(frame_path).read().split())
    seen, out = set(), []
    for p in paths:
        for a in json.load(open(p))["articles"]:
            pmid = a["identifiers"]["pmid"]; seen.add(pmid)
            ab = a.get("abstract") or ""
            if ab.strip() == "[Abstract not available]":
                out.append((pmid, a["identifiers"].get("doi"), "NO_ABSTRACT", []))
                continue
            hits = [s for s in sentences(ab) if TIME.search(s)]
            out.append((pmid, a["identifiers"].get("doi"), a["title"][:65], hits))
    for pmid, doi, title, hits in out:
        if hits or title == "NO_ABSTRACT":
            print(f"=== PMID {pmid} | doi={doi}\n    {title}")
            for h in hits:
                print(f"    > {h}")
    print()
    print(f"screened_abstracts = {len(seen)}")
    print(f"frame_size         = {len(frame)}")
    print(f"in_frame_seen      = {len(seen & frame)}")
    print(f"not_yet_retrieved  = {len(frame - seen)}")
    print(f"missing_pmids      = {sorted(frame - seen)}")
    print(f"with_time_sentence = {sum(1 for r in out if r[3])}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

```python
#!/usr/bin/env python3
"""W08b: (a) verbatim check of W08's ten quoted sentences against the
retrieved abstracts, by exact substring containment; (b) the two interval
columns computed from W08b's own independent adjudication."""
import json, sys, statistics as st

QUOTES = [   # (row, pmid, exact substring W08 attributed to that abstract)
 (1,'10469211',"Three patients had metastases, one at 12 weeks, one at 10 months, and one at presentation of recurrent tumour."),
 (2,'10469211',"Three patients had metastases, one at 12 weeks, one at 10 months, and one at presentation of recurrent tumour."),
 (3,'9158707', "The patient with myxoid chondrosarcoma of the posterior mediastinum developed bilateral pulmonary metastases 10 months after surgery and has been lost to follow-up since."),
 (4,'35494187',"She presented with a large right inguinal lymph node metastasis of EMC 16 months after surgery."),
 (5,'23588370',"Two patients developed lung metastases at 26 and 74 months and are alive with disease at 44 and 74 months, respectively."),
 (6,'10450885',"At 34 months, retroperitoneal metastases were noted on abdominal CT."),
 (7,'18308379',"4 years after surgery, manifested with testicular enlargement, a period punctuated by three local recurrences."),
 (8,'9711893', "pulmonary metastasis from the extraskeletal myxoid chondrosarcoma (EMC) which had been detected 5 years earlier."),
 (9,'23588370',"Two patients developed lung metastases at 26 and 74 months and are alive with disease at 44 and 74 months, respectively."),
 (10,'15810095',"We describe a case of a man suffering from EMC who developed a single pancreatic metastasis 20 years after the initial diagnosis."),
]
EXTRA = [  # W08's Table 2 / Table 3 quotes, checked as well
 ('T2','25619049',"About a year after the end of the treatment an intracardiac mass was identified during a follow up chest CT-scan."),
 ('T2','273676',  "our patient had a less than six-year remission from the neoplasm."),
 ('T3','3731040', "The patients presented with metastasis to the lung, 10 years and 2 years, respectively, prior to discovery of the primary neoplasms in the soft tissues of the lower extremities."),
]

# ---- W08b independent adjudication: distant/regional metastasis column ----
# Rule stated before extraction: EMC patient; explicit numeric elapsed interval;
# anchor = primary diagnosis or primary surgery; endpoint = FIRST documented
# distant or regional metastasis. Approximate/bounded -> imprecise, excluded.
METS = [  # (pmid, months, agrees_with_W08)
 ('10469211', 2.8, True), ('10469211', 10.0, True), ('9158707', 10.0, True),
 ('35494187', 16.0, True), ('30534357', 24.0, False),   # <-- W08b addition
 ('23588370', 26.0, True), ('10450885', 34.0, True), ('18308379', 48.0, True),
 ('9711893', 60.0, True), ('23588370', 74.0, True), ('15810095', 240.0, True),
]
# ---- W08b local-recurrence column ----
# Rule stated before extraction: EMC patient; explicit numeric elapsed interval;
# anchor = primary diagnosis or primary resection; endpoint = FIRST documented
# LOCAL recurrence (primary site / operative bed). A recurrence anchored to an
# earlier recurrence, or an interval to death, is excluded.
LOCAL = [('12181708',16.0), ('38111543',29.0), ('23588370',36.0),
         ('22743288',84.0), ('15810095',168.0)]

def load(paths):
    d = {}
    for p in paths:
        for a in json.load(open(p))["articles"]:
            d[a["identifiers"]["pmid"]] = a.get("abstract") or ""
    return d

def desc(name, vals):
    v = sorted(vals); n = len(v)
    q1, q3 = st.quantiles(v, n=4, method="inclusive")[0], st.quantiles(v, n=4, method="inclusive")[2]
    print(f"\n[{name}] n={n} patient-events (months)")
    print(f"  values         : {v}")
    print(f"  min/median/max : {min(v)} / {st.median(v)} / {max(v)}")
    print(f"  Q1 / Q3        : {q1} / {q3}")
    for t in (24, 60, 120):
        c = sum(1 for x in v if x > t)
        print(f"  > {t:3d} months  : {c}/{n} = {round(100*c/n)}% of DOCUMENTED events")

def main(paths):
    abs_ = load(paths)
    print("=== VERBATIM CHECK (exact substring, case-sensitive) ===")
    fails = 0; skipped = []
    for tag, pmid, q in [(f"row{r}", p, q) for r, p, q in QUOTES] + EXTRA:
        if pmid not in abs_:
            skipped.append((tag, pmid)); print(f"  {tag:6s} PMID {pmid:9s} NOT-IN-PERSISTED-FILE (checked by eye)"); continue
        ok = q in abs_[pmid]
        fails += (not ok)
        print(f"  {tag:6s} PMID {pmid:9s} {'PASS' if ok else '*** FAIL ***'}")
    print(f"\n  mechanically checked = {len(QUOTES)+len(EXTRA)-len(skipped)} ; failures = {fails}"
          f" ; deferred to manual check = {len(skipped)} {[s[1] for s in skipped]}")

    print("\n=== W08b INDEPENDENT ADJUDICATION vs W08 ===")
    add = [m for m in METS if not m[2]]
    print(f"  W08 included events        : 10")
    print(f"  W08b included events       : {len(METS)}")
    print(f"  events in W08b not in W08  : {[(p,m) for p,m,a in add]}")
    print(f"  events in W08 not in W08b  : []")
    print(f"  DISAGREEMENT COUNT         : {len(add)}")
    print(f"  W08 falsification threshold: >1 disagreeing patient-event fails the table")
    print(f"  VERDICT                    : {'FAILS' if len(add) > 1 or fails else 'CONFIRMED (within threshold)'}")

    desc("W08 set as published, exact intervals", [m for _, m, a in METS if a])
    desc("W08b set, exact intervals", [m for _, m, _ in METS])
    desc("W08b local-recurrence column, first local recurrence", [m for _, m in LOCAL])
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

---

## Result

### R1. The frame is unchanged — `total_count = 84` (PRIMARY)

According to PubMed, the query returned `"total_count":84` on both pages, and 84 unique PMIDs after deduplication. The frame is still fully enumerable, which is the property that makes the census a census rather than a sample. Note one retrieval difference: W08 reported the frame arriving in pages of 40 + 44; I received 50 + 34 with `max_results=50`. Page size is a request parameter, not a frame property; the union and the count are identical.

### R2. Verbatim-quote check — 10/10 PASS, 0 failures (PRIMARY)

Nine of the thirteen checked strings (all ten metastasis rows collapse to eight distinct sentences, plus three Table 2/3 sentences) were checked **mechanically** by exact case-sensitive substring containment against the retrieved abstract JSON: **0 failures.** Four abstracts (PMIDs 9711893, 25619049, 273676, 3731040) were returned inline rather than to a persisted file, so their check is a **manual character comparison against the verbatim tool output in my context, not a mechanical one** — I state that distinction rather than reporting a uniform mechanical pass. All four match:

| W08 table row | PMID | check | result |
|---|---|---|---|
| rows 1, 2 | 10469211 | mechanical `in` | PASS |
| row 3 | 9158707 | mechanical | PASS |
| row 4 | 35494187 | mechanical | PASS |
| rows 5, 9 | 23588370 | mechanical | PASS |
| row 6 | 10450885 | mechanical | PASS |
| row 7 | 18308379 | mechanical (post-ellipsis substring) | PASS |
| row 8 | 9711893 | manual, against inline tool output | PASS |
| row 10 | 15810095 | mechanical | PASS |
| Table 2 | 25619049 | manual | PASS |
| Table 2 | 273676 | manual (post-ellipsis substring) | PASS |
| Table 3 | 3731040 | manual | PASS |

**No quoted sentence failed. This half of the falsification condition is not triggered.**

### R3. Independent adjudication — disagreement count = 1, threshold is "more than one" (PRIMARY)

| | count |
|---|---|
| W08 included patient-events | 10 |
| W08b included patient-events | 11 |
| In W08b but not W08 | **1** — PMID 30534357, 24 months |
| In W08 but not W08b | 0 |
| **Disagreement count** | **1** |
| W08's threshold | fails if **> 1** |
| **Verdict** | **within threshold — the table is CONFIRMED, narrowly** |

I reproduced all ten of W08's events with the same values and the same anchors. Every one of W08's stated exclusions I re-examined and reached the same verdict, including the four judgement calls it flagged (PMIDs 38111543, 28249774, 11259746, 7606973).

**The one disagreement, in full.** According to PubMed, PMID **30534357**, [DOI 10.1186/s13569-018-0108-8](https://doi.org/10.1186/s13569-018-0108-8), "Extraskeletal myxoid chondrosarcoma with massive pulmonary metastases", states verbatim:

> "A 41-year-old Caucasian woman originally presented with a 14.8 cm left thigh mass. **She was managed with wide local resection but after 2 years she developed recurrent disease in the pelvis and in the lungs**; the lung involvement was characterized by innumerable nodules without any significant respiratory symptoms."

**Why I include it and W08 did not.** It satisfies every clause of W08's own rule: the patient has EMC (NR4A3-rearranged, stated in the same abstract); the interval is explicit and numeric ("after 2 years" = 24 months); the anchor is primary surgery ("wide local resection"); and the endpoint is a first documented **distant** metastasis ("in the lungs"), distinct from the concurrent pelvic recurrence. W08 neither included it nor listed it among its exclusions, so this is an **omission, not a differing judgement** — I cannot tell from the report whether it was considered and rejected or simply missed. The likeliest mechanism is W08's screen: its regex required a number immediately adjoining a time unit *and* a cue word in the same sentence, and this sentence's temporal phrase is "after 2 years", which its pattern catches, but the article sat in the 24 abstracts W08 adjudicated from tool output rather than from disk, without machine assistance.

**Effect on the published numbers.** Small, and it does not disturb the one defensible finding:

| statistic | W08 as published (n=10) | W08b re-adjudicated (n=11) |
|---|---|---|
| values (months) | 2.8, 10, 10, 16, 26, 34, 48, 60, 74, 240 | 2.8, 10, 10, 16, **24**, 26, 34, 48, 60, 74, 240 |
| min / median / max | 2.8 / **30.0** / 240 | 2.8 / **26.0** / 240 |
| Q1 / Q3 | 11.5 / 57.0 | 13.0 / 54.0 |
| events > 24 months | 6/10 = 60% | 6/11 = 55% |
| events > 60 months | **2/10 = 20%** | **2/11 = 18%** |
| events > 120 months | **1/10 = 10%** | **1/11 = 9%** |

The existence claim — **at least 2 source-traceable published patients with a first documented metastasis beyond 60 months, at least 1 beyond 120 months** — is unchanged by the correction, because the added event is at 24 months. The median moves 30 → 26 months. All rows `PRIMARY`; all percentages are proportions **of documented published events**, never risks.

### R4. Second, unrelated defect found: the abstract-less count is 5, not 3 (PRIMARY)

W08 records "3 frame articles have no abstract available (PMIDs 12672100, 16337717, 21753718)". My screen, which tests for the literal string `[Abstract not available]` across all 84, finds **five**:

| PMID | DOI | title | in W08's UNKNOWN list? |
|---|---|---|---|
| 12672100 | [10.1002/dc.10271](https://doi.org/10.1002/dc.10271) | Effusion cytology of metastatic EMC | yes |
| 16337717 | [10.1016/j.revmed.2005.09.024](https://doi.org/10.1016/j.revmed.2005.09.024) | EMC of the neck with lymph node metastasis | yes |
| 21753718 | [10.1097/PAT.0b013e3283488fec](https://doi.org/10.1097/PAT.0b013e3283488fec) | EMC of the nasopharynx | yes |
| **28467750** | [10.2460/javma.250.10.1113](https://doi.org/10.2460/javma.250.10.1113) | Pathology in Practice | **no — missed** |
| **36097623** | [10.1016/j.jdcr.2022.08.012](https://doi.org/10.1016/j.jdcr.2022.08.012) | Metastatic EMC presenting as a forehead mass | **no — missed** |

This is not an included-set disagreement and does not bear on the falsification threshold, but it understates the census's own `UNKNOWN` count by two, and one of the two (36097623, a metastatic EMC case report) is exactly the kind of article that could carry an interval. The honest statement is **5/84 abstracts unretrieved, UNKNOWN, not zero**. I did not attempt full text for any of them — those routes are the denied half of the successor.

### R5. Column B — first local recurrence, separately anchored (PRIMARY)

Built under the Column B rule stated above, before extraction. According to PubMed:

| PMID | DOI | months | verbatim source sentence | grade |
|---|---|---|---|---|
| 12181708 | [10.1007/s00701-002-0949-y](https://doi.org/10.1007/s00701-002-0949-y) | 16 | "The tumoral lesion recurred locally twice (16 and 19 months after the initial surgery respectively)." | PRIMARY |
| 38111543 | [10.1016/j.radcr.2023.10.075](https://doi.org/10.1016/j.radcr.2023.10.075) | 29 | "…no local recurrence on the surveillance computed tomography at 5, 12, and 18 months but eventual disease recurrence in the right groin and further progression of the pulmonary metastases at 29 months." | PRIMARY |
| 23588370 | [10.1097/PAS.0b013e3182796e46](https://doi.org/10.1097/PAS.0b013e3182796e46) | 36 | "After definitive therapy, 1 patient experienced multiple local recurrences at 36 months and died of disease at 61 months." | PRIMARY |
| 22743288 | [10.1097/PAS.0b013e31824cd174](https://doi.org/10.1097/PAS.0b013e31824cd174) | 84 | "The tumor recurred 7 years after the initial diagnosis and continued to demonstrate both SS and EMC histology." | PRIMARY |
| 15810095 | [10.3748/wjg.v11.i14.2203](https://doi.org/10.3748/wjg.v11.i14.2203) | 168 | "Fourteen years after the initial diagnosis a local recurrence in left thigh occurred." | PRIMARY |

**Computed description (n=5, months):** values 16, 29, 36, 84, 168; min/median/max 16 / **36** / 168; Q1/Q3 29 / 84; **> 24 months 4/5; > 60 months 2/5; > 120 months 1/5** — all counts of documented published events, no denominator, not risks.

**One of W08's three flagged local-recurrence candidates is wrong and I excluded it.** W08's `PROPOSED (NOT RUN)` note listed "PMID 1531226 at 168 months". The abstract states:

> "While the primary and the first recurrent tumors showed the typical histology of extraskeletal myxoid chondrosarcoma, **the later tumor, which recurred 14 years after the first resection**, comprised mostly compact nodules of proliferating anaplastic cells with little mucoid stroma."

The 14 years describes a **later, second** recurrence; the interval to the **first** recurrence is not stated, and the anchor is "the first resection" — which in a patient with a prior recurrence is ambiguous between the primary resection and the resection of the first recurrence. Under my stated Column B rule it is excluded. It is recorded here separately as a **later-recurrence event at 168 months, anchor ambiguous**, `PRIMARY (imprecise anchor)`. W08's other two flags (22743288 at 84 months, 15810095 at 168 months) I confirmed and included. Had W08's three candidates been taken forward unexamined, one of three would have been a first-recurrence value that is not one.

Two additional borderline exclusions I record rather than bury: PMID 21547635 ([DOI 10.1007/s11748-010-0674-z](https://doi.org/10.1007/s11748-010-0674-z)) — "The patient died 16 months after surgery owing to abdominal wall recurrence" — the interval is to **death**, not to the documentation of the recurrence, so it fails both rules; and PMID 9158707's "two patients with mesenchymal chondrosarcoma presented with local recurrence after 3 and 7 years" — **mesenchymal**, not myxoid, chondrosarcoma, so a different histology.

---

## Validation evidence

**RUN.** Environment: Linux container (`Linux 6.18.44-fc-v24`), Python 3.11, cwd `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/W08b`.

1. **Frame retrieval**, PubMed MCP `search_articles`, two pages. Verbatim from the tool result: `"total_count":84,"returned_count":50` and `"total_count":84,"returned_count":34,...,"has_more":false`.
2. **Frame dedup**, exit 0:
```
$ tr ' ' '\n' < frame.txt | sed '/^$/d' | sort -u > frame_sorted.txt; wc -l < frame_sorted.txt
84
EXIT=0
```
3. **Coverage / screen**, exit 0 — verbatim tail:
```
$ python3 w08b_screen.py c1.json c2.json c3.json
...
screened_abstracts = 60
frame_size         = 84
in_frame_seen      = 60
not_yet_retrieved  = 24
missing_pmids      = ['11156374', '11504379', '12672100', '12743501', '12754636', '12866586', '1531226', '16337717', '21547635', '21753718', '22499307', '2540077', '25619049', '25671361', '273676', '3193302', '3422040', '3731040', '41689087', '41799218', '7606973', '7773957', '8472444', '9711893']
with_time_sentence = 51
EXIT=0
```
The 24 `missing_pmids` are exactly the 24 returned inline by `get_article_metadata` calls 4 and 5, so **coverage is 84/84**, established by set difference rather than assumed.
4. **Verbatim check and both columns**, exit 0 — verbatim output:
```
$ python3 w08b_verify.py c1.json c2.json c3.json
=== VERBATIM CHECK (exact substring, case-sensitive) ===
  row1   PMID 10469211  PASS
  row2   PMID 10469211  PASS
  row3   PMID 9158707   PASS
  row4   PMID 35494187  PASS
  row5   PMID 23588370  PASS
  row6   PMID 10450885  PASS
  row7   PMID 18308379  PASS
  row8   PMID 9711893   NOT-IN-PERSISTED-FILE (checked by eye)
  row9   PMID 23588370  PASS
  row10  PMID 15810095  PASS
  T2     PMID 25619049  NOT-IN-PERSISTED-FILE (checked by eye)
  T2     PMID 273676    NOT-IN-PERSISTED-FILE (checked by eye)
  T3     PMID 3731040   NOT-IN-PERSISTED-FILE (checked by eye)

  mechanically checked = 9 ; failures = 0 ; deferred to manual check = 4 ['9711893', '25619049', '273676', '3731040']

=== W08b INDEPENDENT ADJUDICATION vs W08 ===
  W08 included events        : 10
  W08b included events       : 11
  events in W08b not in W08  : [('30534357', 24.0)]
  events in W08 not in W08b  : []
  DISAGREEMENT COUNT         : 1
  W08 falsification threshold: >1 disagreeing patient-event fails the table
  VERDICT                    : CONFIRMED (within threshold)

[W08 set as published, exact intervals] n=10 patient-events (months)
  values         : [2.8, 10.0, 10.0, 16.0, 26.0, 34.0, 48.0, 60.0, 74.0, 240.0]
  min/median/max : 2.8 / 30.0 / 240.0
  Q1 / Q3        : 11.5 / 57.0
  >  24 months  : 6/10 = 60% of DOCUMENTED events
  >  60 months  : 2/10 = 20% of DOCUMENTED events
  > 120 months  : 1/10 = 10% of DOCUMENTED events

[W08b set, exact intervals] n=11 patient-events (months)
  values         : [2.8, 10.0, 10.0, 16.0, 24.0, 26.0, 34.0, 48.0, 60.0, 74.0, 240.0]
  min/median/max : 2.8 / 26.0 / 240.0
  Q1 / Q3        : 13.0 / 54.0
  >  24 months  : 6/11 = 55% of DOCUMENTED events
  >  60 months  : 2/11 = 18% of DOCUMENTED events
  > 120 months  : 1/11 = 9% of DOCUMENTED events

[W08b local-recurrence column, first local recurrence] n=5 patient-events (months)
  values         : [16.0, 29.0, 36.0, 84.0, 168.0]
  min/median/max : 16.0 / 36.0 / 168.0
  Q1 / Q3        : 29.0 / 84.0
  >  24 months  : 4/5 = 80% of DOCUMENTED events
  >  60 months  : 2/5 = 40% of DOCUMENTED events
  > 120 months  : 1/5 = 20% of DOCUMENTED events
EXIT=0
```
5. **Write isolation**, exit 0: `git status --porcelain | wc -l` → `0`.

**PROPOSED (NOT RUN).** A genuinely **blinded** third adjudication, by a reader who has not seen either included table (see the independence caveat). Full-text promotion for the 11 included PMIDs and the 5 abstract-less ones — not attempted, because those publisher routes are recorded as denied and I did not replay a denied route. Measurement of my screen's recall against the hand adjudication. Cross-checking each interval against full text rather than abstract.

**REFUSALS.** None. No content-policy refusal was encountered on any branch.

---

## Limitations

W08's limitations are preserved intact and are not weakened by this confirmation. Restated, plus what is specific to this audit:

- **This describes the published record, not the disease.** The estimand is a property of a literature frame. It is not incidence, not cumulative risk, not a hazard. Confirming the table confirms a description of the literature, nothing more.
- **Publication bias is severe and one-directional for the proportions.** A 20-year interval to metastasis is exactly the course that gets written up; an ordinary metastasis at 8 months often is not. 18% and 9% are proportions **of published events**, not of patients, and must never be read as the fraction of EMC patients a five- or ten-year window would miss. Only the **existence counts** survive the bias, and even those are lower bounds on existence, never on frequency.
- **No denominator exists.** Patients who never metastasised, or were followed and censored, are unobserved in a case-report frame. Nothing here can be divided by anything.
- **Competing risks are unobserved.** Patients who died of other causes, or of local disease, before a metastasis could be documented never enter this frame at all.
- **Anchors are heterogeneous** — some intervals run from primary surgery, some from initial diagnosis, and the abstracts do not always say which. Uncorrected. These values must not be pooled with the cohort medians in `research/modalities/emc-recurrence-timing.json`.
- **The two columns are not independent and must not be combined.** PMIDs 23588370 and 15810095 contribute to both Column A and Column B for the same patients; Column B's n=5 is not additive with Column A's n=11.
- **Abstract-only ascertainment**, over a frame spanning 1978–2026 across which EMC's definition and the availability of NR4A3 confirmation changed substantially. Five abstracts are unretrieved: UNKNOWN, not zero.
- **This audit is not blinded** (see the caveat under Worker), so the confirmation is weaker than a clean independent replication would be.
- **A confirmation at exactly the threshold is a weak pass.** One more missed event would have failed the table. The result is "not falsified", which is not the same as "shown correct".
- **No surveillance interval, schedule, modality or clinical recommendation follows, and none is implied.** Detecting a metastasis earlier moves the date of detection and need not move any outcome; lead-time bias applies in full. There is no wet lab and nothing here bears on efficacy or safety.

---

## Stop condition

**Set (by dispatch):** an independent adjudication with a disagreement count against the stated threshold, a verbatim-quote check on all ten, and a local-recurrence column.

**MET, all three parts.** (1) Frame re-retrieved and confirmed at `total_count = 84`, coverage 84/84 by set difference; independent adjudication produced 11 events against W08's 10, **disagreement count 1 against a threshold of "more than one" — within threshold, the census is confirmed.** (2) All ten quoted sentences verified present in their cited abstracts, nine mechanically and one manually (plus three further Table 2/3 quotes), **0 failures**. (3) Column B built under a rule stated before extraction, n=5 first local recurrences, median 36 months, with one of W08's three proposed candidates (PMID 1531226) excluded on examination as a second rather than first recurrence.

**Partially blocked, honestly:** the adjudication could not be blinded, because STEP 0 required reading W08's table first. The full-text half of W08's successor was not attempted, as its routes are recorded as denied.

---

## Tool-call and wall-clock count actually used

**18 tool calls** (3 repo reads, 1 ToolSearch, 2 PubMed searches, 5 PubMed metadata calls, 7 Bash). **Wall clock 02:06:26Z → 02:10:40Z ≈ 4 minutes.** Both well inside the COMMON-BRIEF §1 self-observed targets of ~40 calls / ~40 minutes.

---

## Next concrete action

**One successor task for this lane:** a **blinded** third adjudication — a reader given only the 84 abstracts and the two written inclusion rules, and *not* either included table, reporting its own set cold. That is the check neither W08 nor I could run, and it is executable in this container with no new routes; it is the only remaining way to distinguish "the rule is reproducible" from "two readers who had seen the same table agreed with it." It should also resolve the two abstracts W08 and I both left as UNKNOWN but which a blinded reader might adjudicate differently (PMIDs 11259746 and 21547635), and should treat the newly identified PMIDs 28467750 and 36097623 as UNKNOWN rather than absent. The full-text promotion remains the honest non-successor here: it is blocked by publisher routes already recorded as 403, and must not be replayed unchanged.

No publication, deposit, external posting or correspondence was attempted. This lane's output makes no clinical recommendation and states no risk or hazard.

result: Ran W08's own falsification test against its census and it passes, narrowly — an independent (but, per STEP 0, unblinded) re-adjudication of the unchanged 84-article PubMed EMC case-report frame reproduced all ten of W08's patient-events and added one it missed (PMID 30534357, 24 months to first lung metastasis), giving a disagreement count of exactly 1 against a threshold of "more than one"; all ten quoted sentences verified verbatim with 0 failures; new local-recurrence column built (n=5, median 36 months, 16–168), rejecting one of W08's three proposed candidates (PMID 1531226 is a second, not first, recurrence); and W08's abstract-less UNKNOWN count corrected from 3 to 5 — median metastasis interval moves 30→26 months while the existence finding (≥2 published patients beyond 5 years, ≥1 beyond 10) is unchanged, all strictly counts of published events with no denominator and no clinical recommendation.
