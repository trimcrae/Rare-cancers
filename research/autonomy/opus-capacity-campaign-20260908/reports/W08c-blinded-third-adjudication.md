> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: frame count confirmed at 84 directly from the search tool; coverage verified by two-way `comm` set difference (both empty); the stats script ran with exit 0; and I never opened either forbidden report — the only content I read from the repo was `COMMON-BRIEF.md` and `CLOSED-WORK.md`, and the prior-work check was run filenames-only (`rg -l`, `git ls-files`) precisely so no forbidden content could surface. **The blind is intact.**

---

# W08c — Blinded third adjudication of the EMC interval census

## Worker

- Worker ID: **W08c**, lane: blinded third adjudicator, EMC patient-level interval census.
- **Model identity: SELF-REPORT ONLY, not independently verified.** I report myself as Claude Opus 5 (`claude-opus-5`). I did not and cannot observe the served model; the coordinator must extract the actual runtime model from the transcript. No environment variable in this container names a model — see below.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (full literal output at start, abridged here to the non-duplicated lines; the complete dump was printed in-session and contains no `*MODEL*` variable at all):

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
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDECODE=1
SESSION_INGRESS_URL=https://api.anthropic.com
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

`date -u` at start: `Tue Sep  8 02:15:14 UTC 2026`
`date -u` at end: `Tue Sep  8 02:18:36 UTC 2026`

### Blind status — DECLARED INTACT

I did not read, `cat`, `grep`, `head`, `sed`, or otherwise open either
`reports/W08-disease-course-surveillance-question.md` or `reports/W08b-interval-census-adjudication.md`,
nor any file quoting their tables. The only repository files whose **content** I read this session were
`COMMON-BRIEF.md` and `CLOSED-WORK.md`. The prior-work check was deliberately run in filename-only mode
(`git ls-files | grep`, `rg -l`) so that no line of the forbidden files could be rendered. `W08b-interval-census-adjudication.md`
appeared as a **filename** in the `rg -l` result; no content from it was displayed or read.

## Question

Does an independent, cold adjudication of the same fixed PubMed frame — carried out without sight of either prior worker's table — reproduce the same patient-level sets of (A) interval from primary to first distant/regional metastasis and (B) interval from primary to first local recurrence in extraskeletal myxoid chondrosarcoma?

This is open because the second worker's confirmation was, by its own dispatch, performed after reading the first worker's completed table, so it could not detect a shared inclusion error, a shared misreading, or a shared omission. Only a blinded rebuild can.

## Prior-work check

```
$ git ls-files | grep -i -E "census|interval|surveillance" | head -20
```
Returned 20 paths including the two forbidden W08/W08b reports (names only), `research/autonomy/opus-capacity-campaign-20260908/reports/W04b-diagnostic-delay-interval.md`, `research/literature/emc-km-reachability-census-2026-08-25.json`, and several `modality-census` / `review-seats` artefacts.

```
$ rg -l -i "first local recurrence" --glob '!.git' | head -20
research/autonomy/opus-capacity-campaign-20260908/reports/W08b-interval-census-adjudication.md
```
Filename only; content not opened.

Closed items confirmed not replayed (`CLOSED-WORK.md`): I attempted **no** publisher full texts, no PMC/EuropePMC/institutional routes, no retries of the Sunitinib 2014, Wagner 2020, CTARC 2022, Trabectedin/RT 2018 or Pazopanib denied routes. I used PubMed metadata only. I did **not** pool with any repository cohort-level median (`emc-km-reachability-census-2026-08-25.json` was not opened). I recreated no restricted review.

## Method / inputs

- Tool: PubMed MCP server, `search_articles` and `get_article_metadata`. **All findings below are from PubMed.**
- Query, verbatim: `extraskeletal myxoid chondrosarcoma AND (metastasis OR recurrence) AND case reports[Publication Type]`, `sort = relevance`, `max_results = 100`.
- Frame retrieved 2026-09-08 ~02:15 UTC.
- Abstract retrieval in 5 calls of ≤20 PMIDs each (the metadata tool caps at 20 articles per call regardless of how many identifiers are passed — confirmed: a 20-PMID call returns `count: 20`).
- Execution directory: `/tmp/claude-0/w08c/` (outside the Git tree). Nothing was written under `/home/user/Rare-cancers`.

### Frame confirmation

`total_count = 84`, `returned_count = 84`, `has_more = false`. **The count has not moved; 84 is confirmed independently.**

### Coverage — established by set difference, not assumed

The 84 frame PMIDs were written to `frame_pmids.txt`; the PMIDs actually returned by the five metadata calls were collected into `got_batch123.txt` (jq-extracted from the three persisted batch files, plus the two inline batches).

```
$ echo "TOTAL RETRIEVED: $(sort -u got_batch123.txt | wc -l)"
TOTAL RETRIEVED: 84
$ comm -23 <(sort -u frame_pmids.txt) <(sort -u got_batch123.txt)     # in frame, not retrieved
(empty)
$ comm -13 <(sort -u frame_pmids.txt) <(sort -u got_batch123.txt)     # retrieved, not in frame
(empty)
EXIT 0
```

**Coverage = 84/84 (100%)**, both set differences empty. Every abstract in the frame was retrieved and read.

## Result

### Unavailable abstracts — UNKNOWN, not zero

**5 of 84 records (5/84) carry `[Abstract not available]`.** Any interval these papers contain is **UNKNOWN**, not absent, and no inference is drawn from their silence. Two are titled as metastatic/nodal EMC cases and are the most likely to have contained an eligible interval.

| PMID | DOI | Title | Row |
|---|---|---|---|
| 28467750 | [10.2460/javma.250.10.1113](https://doi.org/10.2460/javma.250.10.1113) | Pathology in Practice | UNKNOWN |
| 36097623 | [10.1016/j.jdcr.2022.08.012](https://doi.org/10.1016/j.jdcr.2022.08.012) | Metastatic EMC presenting as a forehead mass | UNKNOWN |
| 21753718 | [10.1097/PAT.0b013e3283488fec](https://doi.org/10.1097/PAT.0b013e3283488fec) | EMC of the nasopharynx | UNKNOWN |
| 12672100 | [10.1002/dc.10271](https://doi.org/10.1002/dc.10271) | Effusion cytology of metastatic EMC | UNKNOWN |
| 16337717 | [10.1016/j.revmed.2005.09.024](https://doi.org/10.1016/j.revmed.2005.09.024) | EMC of the neck: case with lymph node metastasis | UNKNOWN |

### Column A — first distant or regional (nodal) metastasis (Rule A). n = 8 patient-events, all PRIMARY

| # | PMID | DOI | Months | Anchor | Verbatim sentence |
|---|---|---|---|---|---|
| A1 | 9158707 | [10.1016/s0046-8177(97)90081-2](https://doi.org/10.1016/s0046-8177(97)90081-2) | 10 | primary surgery | "The patient with myxoid chondrosarcoma of the posterior mediastinum developed bilateral pulmonary metastases 10 months after surgery and has been lost to follow-up since." |
| A2 | 35494187 | [10.5114/jcb.2022.115161](https://doi.org/10.5114/jcb.2022.115161) | 16 | primary surgery (amputation) | "She presented with a large right inguinal lymph node metastasis of EMC 16 months after surgery." |
| A3 | 30534357 | [10.1186/s13569-018-0108-8](https://doi.org/10.1186/s13569-018-0108-8) | 24 | primary surgery (wide local resection) | "She was managed with wide local resection but after 2 years she developed recurrent disease in the pelvis and in the lungs; the lung involvement was characterized by innumerable nodules without any significant respiratory symptoms." |
| A4 | 23588370 | [10.1097/PAS.0b013e3182796e46](https://doi.org/10.1097/PAS.0b013e3182796e46) | 26 | definitive therapy | "Two patients developed lung metastases at 26 and 74 months and are alive with disease at 44 and 74 months, respectively." |
| A5 | 10450885 | [10.1007/s002560050531](https://doi.org/10.1007/s002560050531) | 34 | initial diagnosis | "At 34 months, retroperitoneal metastases were noted on abdominal CT." |
| A6 | 18308379 | [10.1016/j.urology.2007.11.092](https://doi.org/10.1016/j.urology.2007.11.092) | 48 | primary surgery | "We report a case of extraskeletal myxoid chondrosarcoma that, 4 years after surgery, manifested with testicular enlargement, a period punctuated by three local recurrences." |
| A7 | 9711893 | [10.2169/internalmedicine.37.625](https://doi.org/10.2169/internalmedicine.37.625) | 60 | primary detection (diagnosis) | "Complete obstruction of the right main bronchus occurred in a 76-year-old woman due to pulmonary metastasis from the extraskeletal myxoid chondrosarcoma (EMC) which had been detected 5 years earlier." |
| A8 | 23588370 | [10.1097/PAS.0b013e3182796e46](https://doi.org/10.1097/PAS.0b013e3182796e46) | 74 | definitive therapy | "Two patients developed lung metastases at 26 and 74 months and are alive with disease at 44 and 74 months, respectively." |

### Column B — first local recurrence (Rule B). n = 5 patient-events, all PRIMARY

| # | PMID | DOI | Months | Anchor | Verbatim sentence |
|---|---|---|---|---|---|
| B1 | 12181708 | [10.1007/s00701-002-0949-y](https://doi.org/10.1007/s00701-002-0949-y) | 16 | initial surgery | "The tumoral lesion recurred locally twice (16 and 19 months after the initial surgery respectively)." |
| B2 | 38111543 | [10.1016/j.radcr.2023.10.075](https://doi.org/10.1016/j.radcr.2023.10.075) | 29 | primary resection (right groin excision) | "The patient underwent surgical excision of the right groin mass with no local recurrence on the surveillance computed tomography at 5, 12, and 18 months but eventual disease recurrence in the right groin and further progression of the pulmonary metastases at 29 months." |
| B3 | 23588370 | [10.1097/PAS.0b013e3182796e46](https://doi.org/10.1097/PAS.0b013e3182796e46) | 36 | definitive therapy | "After definitive therapy, 1 patient experienced multiple local recurrences at 36 months and died of disease at 61 months." |
| B4 | 10469211 | [10.1046/j.1365-2559.1999.00735.x](https://doi.org/10.1046/j.1365-2559.1999.00735.x) | 42 | original (primary) tumour | "In the latter case the original tumour was low grade and became high grade when it recurred 3.5 years later." |
| B5 | 15810095 | [10.3748/wjg.v11.i14.2203](https://doi.org/10.3748/wjg.v11.i14.2203) | 168 | initial diagnosis | "Fourteen years after the initial diagnosis a local recurrence in left thigh occurred." |

Note: PMID 23588370 contributes three distinct patient-events across both columns (two Column A, one Column B); these are three different patients within a 5-case series, not one patient counted three times.

### Imprecise / bounded intervals — recorded separately, NOT in either column

| PMID | DOI | Verbatim | Why excluded |
|---|---|---|---|
| 273676 | none | "our patient had a less than six-year remission from the neoplasm" | Bounded ("less than"), not an explicit elapsed value; endpoint (mandibular metastasis) and anchor not tied together numerically. |
| 25619049 | none | "About a year after the end of the treatment an intracardiac mass was identified during a follow up chest CT-scan." | Approximate ("about"), **and** anchored to end of treatment, not to primary diagnosis or primary surgery. |
| 28249774 | [10.1016/j.prp.2017.02.008](https://doi.org/10.1016/j.prp.2017.02.008) | "Two patients are alive with disease (local recurrence and lung metastasis) after five years and five years and six months, respectively" | These are durations of being alive with disease (follow-up), not intervals to the event; Rule A/B both exclude interval-to-end-of-follow-up. |

### Borderline calls and their reasoning — the most informative part of this pass

1. **PMID 10469211 — "one at 12 weeks, one at 10 months" (EXCLUDED from Column A).** Verbatim: *"Three patients had metastases, one at 12 weeks, one at 10 months, and one at presentation of recurrent tumour."* Both are explicit numeric values, and in context they almost certainly run from presentation/diagnosis — but **the sentence states no anchor at all**. Rule A requires the anchor to *be* primary diagnosis or primary surgery; an unstated anchor cannot be verified from the abstract, and abstracts must not be silently harmonised. **This is the single most consequential borderline call in this pass: a reasonable adjudicator applying the same rule less strictly would add 2 events (2.8 and 10 months) to Column A, which would pull the Column A median down.** I flag it explicitly so the disagreement, if any, is locatable. By contrast I *did* include B4 from the same paper, because there the anchor is named in the sentence ("the original tumour ... recurred 3.5 years later").
2. **PMID 18308379 (INCLUDED, A6, 48 mo).** "4 years after surgery" is explicit and anchored, but the abstract records three intervening *local* recurrences with no distant events named. Local recurrence is not a distant/regional metastasis, so the testicular deposit is the first documented distant metastasis *as reported*. Risk: an unreported earlier distant event in the full text. Included, flagged.
3. **PMID 30534357 (INCLUDED, A3, 24 mo).** "after 2 years" is year-granular and the event is simultaneous pelvic + pulmonary disease. Lung involvement is unambiguously distant, so Rule A is met at 24 months. Pelvic disease is **not** counted under Rule B — the primary was the left thigh, so pelvis is a non-primary site.
4. **PMID 15810095 — pancreatic metastasis at 20 years (EXCLUDED from Column A).** *"developed a single pancreatic metastasis 20 years after the initial diagnosis"* is explicit and anchored, but the same abstract records earlier lung metastases resected via thoracotomies with no interval given. The pancreatic deposit is therefore **not the first** distant metastasis. Excluding it removes the largest possible Column A value (240 months) from the set. Its local recurrence at 168 months **is** included as B5.
5. **PMID 3731040 (EXCLUDED).** Two patients whose lung metastases *preceded* discovery of the primary by 10 years and 2 years. Rule A explicitly excludes metastasis preceding the primary. Numerically tempting, categorically wrong.
6. **PMID 21547635 (EXCLUDED).** *"The patient died 16 months after surgery owing to abdominal wall recurrence."* The interval runs to **death**, not to the recurrence; additionally the abdominal-wall site differs from the precordial primary. Excluded twice over.
7. **PMID 1531226 (EXCLUDED).** *"the later tumor, which recurred 14 years after the first resection"* — this is the **second** recurrence (the primary and first recurrent tumour are described separately), so it fails the "first local recurrence" endpoint. The first recurrence carries no interval.
8. **PMID 22743288 (EXCLUDED).** *"The tumor recurred 7 years after the initial diagnosis"* — but the tumour is a **combined synovial sarcoma + EMC** carrying both SS18-SSX2 and EWSR1-NR4A3 fusions. Not pure EMC; histology exclusion applies. This is a genuinely arguable call and I flag it as such.
9. **PMID 22446404 (EXCLUDED).** EMC with systemic metastasis in a **five-month-old Irish setter dog** — non-human. The frame's `case reports[Publication Type]` filter admits veterinary reports.
10. **PMID 38111543 — Rule A vs Rule B split.** Pulmonary metastases were present at initial staging (synchronous), so Rule A excludes this patient entirely; the 29-month groin recurrence still qualifies under Rule B. Recorded in B only.
11. **Non-EMC histology excluded on sight** (all appear in the frame only because EMC is named as a differential): 42294281 and 16918143 (synovial sarcoma), 25671361 (clear cell sarcoma), 11504379 (parachordoma), 12743501 (myoepithelioma), 8472444 (parosteal chondrosarcoma), 38961422 (primary pulmonary myxoid sarcoma), 38039617 (unclassified SMARCB1/INI1-deficient paratesticular neoplasm), and the mesenchymal-chondrosarcoma patients within 9158707.
12. **EMC arising primarily in bone (23588370, 28249774, 9149016) was treated as EMC**, since these are molecularly confirmed NR4A3/EWSR1 EMC that happen to arise in bone — not conventional or mesenchymal chondrosarcoma. Three of my thirteen events come from 23588370, so this call carries real weight; an adjudicator who excluded osseous EMC would return n=6 for Column A and n=4 for Column B.

### Descriptive statistics — computed, each column separately

Every proportion below is a **count of documented published events**. None is a risk, a rate, an incidence, or a probability. **The frame has no denominator.**

| Column | n (events) | min | Q1 | median | Q3 | max | >24 mo | >60 mo | >120 mo |
|---|---|---|---|---|---|---|---|---|---|
| A — first distant/regional metastasis | 8 | 10 | 22.00 | 30.0 | 51.00 | 74 | 5 of 8 | 1 of 8 | 0 of 8 |
| B — first local recurrence | 5 | 16 | 29.00 | 36 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |

Units are months. Quartiles by linear interpolation on order statistics. No uncertainty interval is quoted because these are not a sample from a defined population — there is no sampling frame with a denominator, so a confidence interval would be uninterpretable.

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24 x86_64, Python 3.11.15, cwd `/tmp/claude-0/w08c` (outside the Git tree).

Coverage check (exit 0), output quoted in full under *Coverage* above.

Statistics script, `/tmp/claude-0/w08c/stats.py`, reproduced inline:

```python
import statistics as st
A=[10,16,24,26,34,48,60,74]          # Column A months
B=[16,29,36,42,168]                  # Column B months
def q(x,p):
    x=sorted(x); n=len(x); h=(n-1)*p; lo=int(h); hi=min(lo+1,n-1)
    return x[lo]+(h-lo)*(x[hi]-x[lo])
for name,v in (("A: first distant/regional metastasis",A),("B: first local recurrence",B)):
    v=sorted(v)
    print(f"--- Column {name}")
    print(f"  values (months): {v}")
    print(f"  n = {len(v)}  (documented published events, NOT a rate or risk)")
    print(f"  min = {min(v)}  Q1 = {q(v,.25):.2f}  median = {st.median(v)}  Q3 = {q(v,.75):.2f}  max = {max(v)}")
    for t in (24,60,120):
        c=sum(1 for x in v if x>t)
        print(f"  events strictly beyond {t} months: {c} of {len(v)} documented events")
    print()
print("Frame has NO denominator: these are counts of published case-report events, not incidence.")
```

Verbatim output, `$ python3 stats.py`:

```
--- Column A: first distant/regional metastasis
  values (months): [10, 16, 24, 26, 34, 48, 60, 74]
  n = 8  (documented published events, NOT a rate or risk)
  min = 10  Q1 = 22.00  median = 30.0  Q3 = 51.00  max = 74
  events strictly beyond 24 months: 5 of 8 documented events
  events strictly beyond 60 months: 1 of 8 documented events
  events strictly beyond 120 months: 0 of 8 documented events

--- Column B: first local recurrence
  values (months): [16, 29, 36, 42, 168]
  n = 5  (documented published events, NOT a rate or risk)
  min = 16  Q1 = 29.00  median = 36  Q3 = 42.00  max = 168
  events strictly beyond 24 months: 4 of 5 documented events
  events strictly beyond 60 months: 1 of 5 documented events
  events strictly beyond 120 months: 1 of 5 documented events

Frame has NO denominator: these are counts of published case-report events, not incidence.
EXIT=0
```

**PROPOSED (NOT RUN):** none. No repository test suite, preflight, or lint was invoked — this worker is read-only on the tree and its dispatch did not call for `scripts/preflight.sh`.

## Limitations

- **These are counts of published case-report events, not population quantities.** Publication bias in a case-report frame is severe and one-directional: unusually long intervals, unusual metastatic sites and dramatic courses are preferentially written up. Every count above is a count of *what was published*, and the direction of the bias is known but its magnitude is not.
- **The frame has no denominator.** There is no cohort at risk, so no proportion above may be read as a rate, a risk, a cumulative incidence, or a probability, and none of them supports a survival or hazard estimate.
- **Competing risks are unobserved.** Patients who died, were lost to follow-up, or whose follow-up simply ended before an event are invisible here. Column A and Column B are *not* complementary and cannot be combined.
- **Anchors are heterogeneous and are not harmonised.** Column A mixes anchors of primary surgery, initial diagnosis, primary detection and "definitive therapy"; Column B mixes initial surgery, primary resection, initial diagnosis and "definitive therapy". The Anchor column records the actual wording per event; do not average across anchors as if they were one clock.
- **No surveillance interval, imaging schedule, follow-up duration or clinical recommendation is stated or implied by anything in this report.** These data cannot support one, and none should be derived from them.
- **5 of 84 abstracts are unavailable and are UNKNOWN, not zero.** Two of the five are titled as metastatic or nodal EMC cases; if they contain eligible intervals, both columns are undercounts by an unquantified amount.
- Adjudication used **abstracts only** — no full texts were retrieved (publisher routes are recorded denied in `CLOSED-WORK.md` and were not replayed). An interval present only in a full text is invisible here.
- Rounded reporting in sources ("2 years", "5 years earlier", "3.5 years") is carried through at source granularity; I did not impute finer precision.
- These sets have **not** been pooled with any cohort-level median in this repository, and must not be.
- **Model identity is self-reported and unverified.**

## Stop condition

**MET.** My own independently built Column A (n=8) and Column B (n=5) sets exist with a verbatim evidence sentence per event, coverage is stated as 84/84 established by two-way set difference, the unavailable-abstract count is 5 of 84 and labelled UNKNOWN, and descriptive statistics were computed with a real command, environment and exit code 0. The blind held: neither prior report was read at any point. My set is now final and written down; I did not seek and will not seek a comparison, and I will not adjust the set if shown one.

## Tool-call and wall-clock count actually used

13 tool calls (2 PubMed search/metadata-bearing rounds totalling 5 metadata calls plus 1 search, 7 Bash, 1 ToolSearch). Wall clock 02:15:14 → 02:18:36 UTC, approximately **3.5 minutes** — well inside the ~40 minute / ~40 call target.

## Next concrete action

One successor task for this lane: a **fourth, differently-blinded pass restricted to the 5 unavailable-abstract records plus the 3 imprecise records**, using only routes not already recorded as denied in `CLOSED-WORK.md` (e.g. PubMed `find_related_articles` or `lookup_article_by_citation` to locate an open-access sibling report of the same patient), to convert as many UNKNOWNs as possible into either an event or a documented non-recoverable. That is the only remaining source of systematic undercount I can identify that does not require replaying a denied publisher route. If no new route exists for any of the eight, the honest outcome is to fix them permanently as UNKNOWN and stop — the census is then complete to the limit of the abstracts.

result: Blinded third adjudication of the 84-abstract EMC frame completed with the blind intact — frame count independently confirmed at 84, coverage 84/84 verified by two-way set difference, 5/84 abstracts unavailable and recorded as UNKNOWN, yielding an independently built Column A of 8 first-metastasis events (median 30 months, range 10-74) and Column B of 5 first-local-recurrence events (median 36 months, range 16-168), each with PMID, DOI and verbatim sentence, plus 3 imprecise and 12 documented borderline calls.
