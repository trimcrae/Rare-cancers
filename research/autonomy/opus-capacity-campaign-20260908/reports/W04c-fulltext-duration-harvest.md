> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check done: Clopper–Pearson self-test passes against five textbook values, script exits 0, `git status --porcelain` is empty (no writes to the tree), and `rg` confirms the two duration sentences I extracted appear nowhere in the repository despite both papers already being cited there for radiotherapy. Full report follows.

---

## Worker

- **Worker ID:** W04c — refill for the diagnostic-delay lane (Lane 6, diagnostic-delay half). Named successor to W04b.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt, under Claude Code 2.1.42. I did not observe the served model and do not assert it as fact; the coordinator should extract the actual runtime model from the transcript.
- **`date -u` at start:** `Tue Sep  8 02:12:29 UTC 2026` · **at end:** `Tue Sep  8 02:15:51 UTC 2026`
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** — literal output, abridged only by dropping the five long proxy lines (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy`), which match solely because they enumerate `api.anthropic.com` and carry no model identity:

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

No environment variable in this container names a model — same finding W04b and W06 recorded. My identity claim rests solely on my system prompt.

**Write-isolation compliance.** I wrote nothing under `/home/user/Rare-cancers`. All execution happened in `/tmp/claude-0/w04c/`. `git status --porcelain` returns **empty**, and `find . -name '*W04c*' -not -path './.git/*'` returns nothing. No git write operation of any kind was run. No paywalled route was attempted; no 403 was incurred; no content-policy refusal occurred.

---

## Question

**How often does an EMC case report actually record the symptom-to-diagnosis interval, when the denominator is full texts rather than abstracts — and does any source quantify the time a misdiagnosis cost?**

It is open because W04b's headline 7/26 was measured at abstract level and its own 2-of-2 full-text probe showed abstracts undercount. That probe established **direction** with a 95% interval of [0.158, 1.000] — it could not distinguish "abstracts miss a few" from "abstracts miss everything." The magnitude was the named successor task.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers`:

1. `rg -n -i "full.?text|fulltext" research/autonomy/opus-capacity-campaign-20260908/reports/ --glob '!.git' -l`
2. `rg -n -i "35494187|40831041|PMC9044308|PMC12376927|Bartholin|plantar fibroma" --glob '!.git' .`
3. `git ls-files | rg -i "W04|delay|symptom"`
4. `rg -n -i "30 years ago|discovered 30 years|refused to consult|6 years earlier|peanut-sized" --glob '!.git' .`

**What this showed, and it matters.** Command 2 found that **two of the papers carrying my two new duration values are already in the repository** — PMID 35494187 / PMC9044308 (ankle EMC, HDR brachytherapy) appears in `emc-oligometastatic-rt-concept.md`, `emc-radioresistance-reappraisal.md` (marked `[FT]`, i.e. its full text has been read here before), `emc-unexplored-treatment-lanes.md`, `emc-terminal-events-classified.json` and `citation-retraction-sweep.json`; PMID 40831041 / PMC12376927 (buttock EMC) appears in `citation-retraction-sweep.json`, `citation-article-types.json`, `lint_citation_types.py`, the citation-type guard tests, and the fusion-partner correction register (row A11, where it is the misattributed "review literature" identifier). **Every one of those uses is radiotherapy dose, terminal events, or citation-type hygiene. None is about symptom duration.** Command 4 confirms it: the strings `30 years ago`, `discovered 30 years`, `refused to consult`, `6 years earlier` and `peanut-sized` return **zero hits repository-wide**. So the papers are known here and the duration sentences in them are not. That is an instructive miss in its own right — the repository read PMC9044308's full text for a brachytherapy dose and walked past a stated 30-year symptom duration in the same paragraph.

Command 3 confirms W04b's report is now tracked, and command 1 confirms no other campaign report has done a full-text reporting-rate measurement.

**Closed items confirmed not replayed.** I opened no route to Wagner 2020, CTARC 2022, Sunitinib 2014, the Pazopanib primary, or Trabectedin/RT 2018. I did not touch GSE4303/GSE28866, the NR4A Perspective, the ICD-O classification paper, or the clinical registry. **W04b's negative is preserved intact and is not weakened anywhere below** — see the explicit preservation statement in Result.

---

## Method / inputs

**Retrieval — PubMed MCP tools only** (`convert_article_ids`, `get_full_text_article`, `get_article_metadata`). No WebSearch, no publisher route, no paywall attempt, no route recorded as denied.

- `convert_article_ids` on all 16 W04b `SILENT_CASES` PMIDs → 8 carry a PMCID, 8 carry none.
- `get_full_text_article` on `["PMC6449903","PMC10519304","PMC5351361"]`, then `["PMC13005408","PMC12376927","PMC12659415"]`, then `["PMC9527174","PMC9044308","PMC6449903"]` (PMC6449903 deliberately retried once).
- `get_article_metadata` on the 8 PMIDs with no PMCID, to identify them and confirm the unrecovered set.

**A correction to the dispatch prompt's stated PMC list.** The prompt named PMC10908772 and PMC5011171 among these 16. The NCBI ID converter returns **neither** for any of the 16 PMIDs. The eight real PMCIDs are PMC13005408, PMC12376927, PMC12659415, PMC10519304, PMC9527174, PMC9044308, PMC6449903, PMC5351361. I used the converter's output, not the prompt's list.

**Attribution (required by the PubMed tool's terms).** According to PubMed and PubMed Central, all article facts below were retrieved from PubMed. DOI links: PMID 41689087 [DOI](https://doi.org/10.1186/s12957-026-04247-0); PMID 40831041 [DOI](https://doi.org/10.12659/AJCR.947135); PMID 41323055 [DOI](https://doi.org/10.1159/000548238); PMID 39924782 [DOI](https://doi.org/10.1111/jog.16235); PMID 37753118 [DOI](https://doi.org/10.13107/jocr.2023.v13.i09.3858); PMID 35974707 [DOI](https://doi.org/10.1111/1759-7714.14613); PMID 35494187 [DOI](https://doi.org/10.5114/jcb.2022.115161); PMID 33075019 [DOI](https://doi.org/10.1097/PGP.0000000000000723); PMID 30967942 [DOI](https://doi.org/10.3892/mco.2019.1822); PMID 28360467 [DOI](https://doi.org/10.4103/0970-2113.201312); PMID 26504046 (Lockyer & Rosen, *Anticancer Res* 35:6171-4 — no DOI in the PubMed record); PMID 25550031 [DOI](https://doi.org/10.1177/230949901402200331); PMID 24818862 [DOI](https://doi.org/10.1007/s00256-014-1897-3); PMID 19894252 [DOI](https://doi.org/10.1002/dc.21200); PMID 7648738 [DOI](https://doi.org/10.1097/00003072-199506000-00013); PMID 29886600 [DOI](https://doi.org/10.3760/cma.j.issn.0529-5807.2018.06.022). Carried forward from W04b for the distribution: PMID 26125202 (Lubana) [DOI](https://doi.org/10.12659/AJCR.894804); PMID 21941486 (Mitchell) [DOI](https://doi.org/10.1159/000331237).

**Computation.** One stdlib-only Python 3.11.15 script authored by me, returned inline, run in `/tmp/claude-0/w04c/` outside the repository. Clopper–Pearson via bisection on a continued-fraction regularised incomplete beta.

**Estimand discipline, unchanged from W04b.** Primary-mass symptom duration, metastatic-symptom duration, and metastasis-to-primary interval are three quantities and are never pooled. A value computed from two dated events is DERIVED. An unretrievable full text is UNRECOVERED → UNKNOWN, never a negative, never imputed.

---

## Result

### Table 1 — per-paper full-text outcome for all 16 abstract-silent case reports

| PMID | PMCID | Paper | Outcome | Months | Grade |
|---|---|---|---|---|---|
| 40831041 | PMC12376927 | Buttock EMC, 40 cm | **states duration** | **72** | **PRIMARY** |
| 35494187 | PMC9044308 | Ankle EMC, HDR-ISBT | **states duration** | **360** | **PRIMARY** |
| 28360467 | PMC5351361 | Axilla EMC, lung mets | **states duration (non-numeric)** | — | **PRIMARY (qualitative)** |
| 41689087 | PMC13005408 | Hand EMC, unplanned excision | full text read, silent | — | **PRIMARY (negative)** |
| 41323055 | PMC12659415 | Metastatic EMC, SABR | full text read, silent | — | **PRIMARY (negative)** |
| 37753118 | PMC10519304 | Toe EMC read as fracture | full text read, silent | — | **PRIMARY (negative)** |
| 35974707 | PMC9527174 | Pleural metastases, TME | full text read, silent for primary | — | **PRIMARY (negative)** |
| 30967942 | PMC6449903 | O'Neill, vulval EMC | **UNRECOVERED** — `full_text` returned `""` on two separate calls | — | **UNKNOWN** |
| 39924782 | — | EMC mimicking mucinous ovarian ca. | UNRECOVERED — no PMCID | — | **UNKNOWN** |
| 33075019 | — | Vulval EMC, EWSR1 FISH | UNRECOVERED — no PMCID | — | **UNKNOWN** |
| 26504046 | — | Lockyer, EMC as plantar fibroma | UNRECOVERED — no PMCID | — | **UNKNOWN** |
| 25550031 | — | Paediatric thigh EMC | UNRECOVERED — no PMCID | — | **UNKNOWN** |
| 24818862 | — | Femoral-vein EMC | UNRECOVERED — no PMCID | — | **UNKNOWN** |
| 19894252 | — | FNA cytology of EMC | UNRECOVERED — no PMCID | — | **UNKNOWN** |
| 7648738 | — | Radionuclide imaging in EMC | UNRECOVERED — no PMCID | — | **UNKNOWN** |
| 29886600 | — | Yue 2018, corpus callosum (Chinese) | UNRECOVERED — no PMCID **and** no abstract | — | **UNKNOWN** |

**7 of 16 full texts read; 9 UNRECOVERED.** Every unrecovered row is UNKNOWN and none is counted as a negative. Only open-access PMC was attempted, per the brief.

### Table 2 — every symptom-duration sentence found, verbatim

| PMID | Estimand | Value | Verbatim |
|---|---|---|---|
| 40831041 | **primary mass** | **72 mo** | *"a subcutaneous mass on his right buttock, which had **gradually increased in size over 6 years**, and was accompanied by redness, swelling, and ulceration over the previous 2 weeks"* and *"The patient reported **first palpating a peanut-sized subcutaneous mass** that was non-tender on his right buttock **6 years earlier**."* |
| 40831041 | other (symptom escalation) | 0.5 mo | *"Two weeks before presentation, he noticed redness and ulceration"* — excluded from the primary distribution |
| 35494187 | **primary mass** | **360 mo** | *"An 87-year-old woman presented with a **slow-growing tumor of the right ankle joint discovered 30 years ago**. **She refused to consult a doctor because she only experienced few symptoms.** In 2015, the patient's ankle joint tumor underwent necrosis with infection, and **she was diagnosed with EMC** of the right ankle joint based on biopsy results."* |
| 28360467 | **primary mass** | **qualitative only** | *"presented with complaints of right upper extremity pain while lifting heavy objects at work, **from several months**"* |
| 28360467 | metastasis | qualitative | *"He also complained of **cough and hemoptysis for the past several weeks**"* — different estimand, excluded |
| 35974707 | metastasis interval | 36 mo | *"**Three years earlier**, she had undergone surgery and radiotherapy for EMCS of the right knee at another hospital"* — treatment-to-metastasis, **not** symptom-to-diagnosis; excluded |
| 41689087 | ambiguous | — | *"A 46-year-old man presented with a mass on the dorsum of the left hand **2-years ago**."* The identical construction appears for Case 2 (a synovial sarcoma), so this dates the *presentation event* relative to writing, not the duration of symptoms. **Graded silent, not a duration statement.** |
| 37753118 | none | — | *"complaints of the left 3rd toe pain and swelling that **began after a traumatic impact to the foot while walking**"* — acute onset, no interval |
| 41323055 | none | — | *"A 39-year-old woman from Sri Lanka was **diagnosed in 2019**"* — no symptom onset given |

**Note on 35494187.** The 30-year value is stated, unambiguous, and explicitly attributed by the authors to **patient-side non-presentation** (*"She refused to consult a doctor"*). It is the single longest symptom duration in the entire retrievable EMC record, and it was invisible from the abstract.

### Table 3 — W04b's Table 3, recomputed on a full-text denominator ★ the deliverable

| Quantity | k/n | Proportion [95% Clopper–Pearson] | Grade |
|---|---|---|---|
| **Abstract-silent case reports whose full text states a duration — W04c** | 3/7 | 0.429 [0.099, 0.816] | **PRIMARY** |
| W04b probe alone, for reference | 1/2 | 0.500 [0.013, 0.987] | **PRIMARY** |
| **COMBINED, strict (duration actually stated)** | **4/9** | **0.444 [0.137, 0.788]** | **PRIMARY** |
| COMBINED, lenient (+ Mitchell's DERIVED value) | 5/9 | 0.556 [0.212, 0.863] | **SECONDARY (derived included)** |

W04b's probe re-scored strictly gives 1/2, not 2/2, because Mitchell 2011 states no duration — its value is derived from two dated events, and W04b itself graded it DERIVED. The combined strict denominator is 9 abstract-silent case reports whose full text was read (Lubana, Mitchell, and my seven).

**The measurement.** *Roughly 44% of abstract-silent EMC case reports state a symptom duration in their full text* — **not** 100%. **1.000 lies above the 95% upper limit of 0.788, so W04b's 2/2 result is not sustained at n=9.** W04b's direction finding survives — abstracts do undercount, materially — but its magnitude was a small-sample artefact. Slightly more than half of abstract-silent EMC case reports are silent in their full text too.

**Consequent bound on the overall reporting rate (no imputation).**

| Quantity | Value | Grade |
|---|---|---|
| W04b lower bound, abstract level | 7/26 = 0.269 | PRIMARY (superseded as a bound) |
| **W04c lower bound, abstract + full texts read** | **11/26 = 0.423 [95% CP 0.234, 0.631]** | **PRIMARY** |
| Case reports whose full text was never read → status UNKNOWN | 10/26 | **UNKNOWN** |
| **Interval of ignorance** (all 10 unknowns negative ↔ all positive) | **[0.423, 0.808]** | **PRIMARY (bound, not a CI)** |

11/26 is still a **lower bound**, now a considerably tighter one. The [0.423, 0.808] interval is arithmetic over what is known and unknown — it is not a sampling interval and must not be read as one.

### Table 4 — the case-report distribution, enlarged, and still not a delay estimate

| Set | n | Median | Range | Values (months) |
|---|---|---|---|---|
| Stated durations only | **10** | **9.0 mo** | 2–360 | 2, 5, 6, 6, 6, 12, 12, 36, **72**, **360** |
| + 1 derived from dates | 11 | 6.0 mo | 2–360 | 2, 5, 6, 6, 6, 6, 12, 12, 36, 72, 360 |

W04b had n=8, median 6.0, range 2–36. **Both new values sit in the extreme right tail, and both were invisible from abstracts.** The stated-only median moves 6.0 → 9.0 months and the range extends 2–36 → 2–360 months. This is the sharpest form of W04b's warning: an abstract-level harvest did not merely undercount, it **truncated precisely the tail that a delay analysis would care about**. Whatever selection puts a duration into an abstract, it is not the selection that puts a 30-year or 6-year history into a case report.

**Labelled exactly as W04b labelled it, and for the same reason.** This is a distribution over **publication decisions, not over patients**. Its denominator is the case reports that chose to state a duration. The selection runs hard toward the unusual: a 40 cm ulcerated buttock mass, a 30-year untreated ankle tumour in an 87-year-old who declined care, a nasopharynx, a masticator space, a floor of mouth, a plantar fascia, a chest wall, a lung primary, a paediatric leg. The larger n does not make it a delay estimate; if anything the two new points make the selection toward the extraordinary more visible, not less. **The median of 9 months cannot be read as a median diagnostic delay for EMC.**

### W04b's negative, preserved intact

Nothing here touches the series-level finding, and it stands unchanged and unweakened: **0 of 8 retrievable EMC series report a symptom-duration statistic with a denominator; 324 of 331 pooled patients (97.9%) sit in a source that states nothing at all; the sole cohort statement is Xu 2014's bare 3–12 month range over n=5 with an UNSTATED non-missing denominator.** My work is entirely at the case-report level and adds no cohort denominator. The overall conclusion — that the published EMC record cannot support a symptom-duration or diagnostic-delay distribution, because the interval is not systematically collected — is **unchanged**. What has changed is that the *case-report* half of that record is better characterised, and worse-behaved, than the abstract harvest suggested.

### The system-side delay verdict ★ explicit

| Narrative | PMID | Retrieval | Does it quantify the time the misreading cost? |
|---|---|---|---|
| O'Neill — vulval EMC managed as a Bartholin's cyst | 30967942 | **UNRECOVERED** (PMC returned an empty body twice) | **UNKNOWN.** Abstract asserts *"initially misdiagnosed as a Bartholin's cyst and managed conservatively"* and that *"patients may incur delays in diagnosis and treatment"*, and gives a presentation year (2011) — but no diagnosis date and no interval. |
| Toe EMC read as a traumatic fracture | 37753118 | full text read | **NO.** *"The erosive changes and osseous lesions were initially misdiagnosed as a fracture."* The narrative runs ED → orthopaedic referral → radiographs → MRI → bone scan → open biopsy → amputation with **no date and no interval anywhere**. |
| Lockyer — plantar EMC read as a plantar fibroma | 26504046 | **UNRECOVERED** (no PMCID, *Anticancer Res*) | **UNKNOWN.** Abstract says *"initially thought to be a plantar fibroma"*; no interval there. |
| Hand EMC *"considered benign"*, unplanned excision elsewhere (found incidentally this run) | 41689087 | full text read | **NO.** *"The tumor was considered benign and resected at another hospital. However, the pathological diagnosis based on the surgical specimen was extraskeletal myxoid chondrosarcoma and the patient was referred to our hospital."* No interval between the unplanned excision and the referral. |

**VERDICT: no source quantifies a system-side diagnostic delay.** Zero of four retrievable EMC misdiagnosis narratives states the time the misreading cost. The one long interval that *is* quantified anywhere — the 30 years in PMID 35494187 — is explicitly **patient-side**, attributed by its own authors to a patient who declined to consult a doctor, and is therefore not a system-side interval.

This is a negative over what was **read**, not proof of universal absence: two of the four narratives (O'Neill, Lockyer) remain UNRECOVERED, and O'Neill in particular — a paper whose title is *"A 5-year follow-up"* and whose abstract raises diagnostic delay by name — is the single most likely place in this literature for such a number to exist. **It stays UNKNOWN.**

### The answer

1. **The reporting rate on a full-text denominator is 4/9 = 0.444 [95% CP 0.137, 0.788].** Abstracts undercount EMC symptom-duration reporting, but by roughly a factor of two, not by everything. W04b's 2/2 = 1.000 does not survive the enlarged probe.
2. **The overall case-report reporting rate is bounded at [0.423, 0.808], with 11/26 now known-positive and 10/26 still UNKNOWN.** The lower bound moved 0.269 → 0.423 and remains a lower bound.
3. **The abstract-level harvest was biased in shape, not only in count** — it truncated the right tail, losing both of the corpus's longest durations (6 years, 30 years).
4. **No system-side delay interval exists in the retrievable literature.** The mechanism (myxoid confusability, misdiagnosis as Bartholin's cyst / fracture / plantar fibroma / benign tumour) is attested in four separate papers; its magnitude is measured in none of them. W04b's constraint therefore holds and is now better evidenced: **any claim that diagnostic delay drives EMC presentation stage remains unsupported by the primary literature in either direction.**

---

## Validation evidence

**RUN.**

- Working directory `/tmp/claude-0/w04c` — outside the repository, per the corrected brief.
- Environment: `Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]`, `Linux 6.18.44-fc-v24 x86_64`
- Command: `date -u && python3 -VV && uname -srm && python3 emc_fulltext_reporting.py; echo "EXIT=$?"` → **`EXIT=0`**

**Interval implementation verified before use, as instructed.** W04b found and fixed an inverted Clopper–Pearson quantile. I did not assume the fix and I did not trust my own transcription of it: the script's `selftest()` runs **first**, asserts, and would abort the whole run on failure. It checks five textbook two-sided 95% values, including both boundary cases (k=0 and k=n) where an inversion shows up most loudly, and asserts `lower <= upper` on every one. Verbatim:

```
[0] INTERVAL IMPLEMENTATION CHECK (W04b fixed an inverted quantile here)
  Clopper-Pearson self-test against textbook two-sided 95% values:
    k= 0 n=10: [0.0000, 0.3085]  expected [0.0000, 0.3085]  OK
    k=10 n=10: [0.6915, 1.0000]  expected [0.6915, 1.0000]  OK
    k= 2 n=10: [0.0252, 0.5561]  expected [0.0252, 0.5561]  OK
    k= 1 n=10: [0.0025, 0.4450]  expected [0.0025, 0.4450]  OK
    k= 5 n=10: [0.1871, 0.8129]  expected [0.1871, 0.8129]  OK
  self-test PASS (monotone, lower<=upper, matches textbook)
```

As an independent cross-check, the script reproduces W04b's own published intervals exactly where the inputs are the same: `k=7 n=26 → [0.116, 0.478]` and `k=2 n=2 → [0.158, 1.000]`. **I did trust the interval implementation after this check, and only after it.**

Verbatim key output of the run:

```
[1] FULL-TEXT RETRIEVAL OUTCOMES FOR THE 16 ABSTRACT-SILENT CASE REPORTS
  FULLTEXT_STATED_NUMERIC       : 2
  FULLTEXT_STATED_QUALITATIVE   : 1
  FULLTEXT_SILENT               : 4
  UNRECOVERED                   : 9
  full texts actually READ                : 7 / 16
  UNRECOVERED (UNKNOWN, not a negative)   : 9 / 16

[2] REPORTING RATE ON A FULL-TEXT DENOMINATOR  *** the deliverable ***
  this run only (W04c)            : 3/7 = 0.429  [95% CP 0.099, 0.816]
  W04b probe only (for reference) : 1/2 = 0.500  [95% CP 0.013, 0.987]
  COMBINED, strict (stated)       : 4/9 = 0.444  [95% CP 0.137, 0.788]
  COMBINED, lenient (+DERIVED)    : 5/9 = 0.556  [95% CP 0.212, 0.863]
  => W04b's 2/2 = 1.000 is NOT sustained: 1.0 lies ABOVE the upper limit 0.788.

[3] W04b TABLE 3, RECOMPUTED -- bound, not point estimate (no imputation)
  now KNOWN to state a primary-mass duration       : 11
  full text still never read -> status UNKNOWN     : 10
  W04b lower bound (abstract level)                : 7/26 = 0.269
  W04c lower bound (abstract + full text read)     : 11/26 = 0.423  [95% CP 0.234, 0.631]
  interval of IGNORANCE (all unknowns -/+)         : [0.423, 0.808]

[4] CASE-REPORT DISTRIBUTION, ENLARGED  (*** NOT a delay estimate ***)
  stated durations only    n=10  median=   9.0 mo  range=2-360 mo  values=[2, 5, 6, 6, 6, 12, 12, 36, 72, 360]
  +1 derived from dates    n=11  median=   6.0 mo  range=2-360 mo  values=[2, 5, 6, 6, 6, 6, 12, 12, 36, 72, 360]

[5] SYSTEM-SIDE DELAY (time the misreading cost) -- EXPLICIT VERDICT
  VERDICT: 0 of 4 retrievable misdiagnosis narratives quantifies the time the
           misreading cost. NO system-side diagnostic-delay interval is
           recoverable from this literature. 2 of 4 remain UNRECOVERED, so this
           is a negative over what was READ, not proof of universal absence.
EXIT=0
```

**Read-only compliance, verified:** `git status --porcelain` → **empty**; `find . -name '*W04c*' -not -path './.git/*'` → empty.

**PROPOSED (NOT RUN).** Full-text retrieval of the 9 UNRECOVERED case reports (all would need paywalled routes, which the brief forbids); a second retrieval route for PMC6449903, whose PMC record exists but whose body came back empty twice — this is a tool-side or deposit-side gap, not a paywall, and may be recoverable by a different open-access route.

### Code (authored by me; returned inline, not written into the tree)

`/tmp/claude-0/w04c/emc_fulltext_reporting.py`, stdlib-only, reproduced in full:

```python
#!/usr/bin/env python3
"""
W04c (OPUS-CAPACITY-CAMPAIGN-20260908) -- full-text-denominator reporting rate for
the EMC symptom-to-diagnosis interval.

Converts W04b's 2/2 abstract-vs-full-text probe into a real measurement by reading
the full texts of the 16 abstract-silent EMC case reports it left as PROPOSED.

Discipline inherited from W04b/W06 and NOT relaxed:
  - a source whose full text could not be retrieved is UNRECOVERED -> UNKNOWN,
    never a negative, never imputed;
  - primary-mass duration, metastatic-symptom duration and metastasis-to-primary
    interval are three different estimands and are never pooled;
  - a value computed from two dated events is DERIVED, not stated.
"""
import statistics as st
import math

# ------------------------------------------------------------ exact binomial
def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 300, 3.0e-16, 1.0e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN: d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS: break
    return h

def betainc(a, b, x):
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    lbeta = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
             + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbeta) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta) * _betacf(b, a, 1.0 - x) / b

def clopper_pearson(k, n, alpha=0.05):
    """low = Beta^-1(alpha/2; k, n-k+1);  high = Beta^-1(1-alpha/2; k+1, n-k)."""
    def _inv(target, a, b):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2.0
            if betainc(a, b, mid) < target: lo = mid
            else: hi = mid
        return (lo + hi) / 2.0
    low = 0.0 if k == 0 else _inv(alpha / 2, k, n - k + 1)
    high = 1.0 if k == n else _inv(1 - alpha / 2, k + 1, n - k)
    return low, high

def selftest():
    """W04b found and fixed an INVERTED quantile here. Verify before trusting."""
    cases = [((0,10),(0.0000,0.3085)), ((10,10),(0.6915,1.0000)),
             ((2,10),(0.0252,0.5561)), ((1,10),(0.0025,0.4450)),
             ((5,10),(0.1871,0.8129))]
    ok = True
    print("  Clopper-Pearson self-test against textbook two-sided 95% values:")
    for (k,n),(elo,ehi) in cases:
        lo,hi = clopper_pearson(k,n)
        good = abs(lo-elo)<5e-4 and abs(hi-ehi)<5e-4 and lo<=hi
        ok &= good
        print(f"    k={k:>2} n={n:>2}: [{lo:.4f}, {hi:.4f}]  expected [{elo:.4f}, {ehi:.4f}]  {'OK' if good else 'FAIL'}")
    assert ok, "Clopper-Pearson self-test FAILED"
    print("  self-test PASS (monotone, lower<=upper, matches textbook)\n")

# --------------------------------------------- the 16 abstract-silent case reports
# outcome: FULLTEXT_STATED_NUMERIC | FULLTEXT_STATED_QUALITATIVE
#          | FULLTEXT_SILENT | UNRECOVERED
PROBE16 = [
 ("41689087","PMC13005408","Reconstruction after unplanned excisions (Case 1, hand EMC)",
  "FULLTEXT_SILENT", None,
  "A 46-year-old man presented with a mass on the dorsum of the left hand 2-years ago."
  " || 'The tumor was considered benign and resected at another hospital. However, the"
  " pathological diagnosis based on the surgical specimen was extraskeletal myxoid"
  " chondrosarcoma and the patient was referred to our hospital for treatment.'"),
 ("40831041","PMC12376927","Large extraosseous myxoid chondrosarcoma of the buttocks",
  "FULLTEXT_STATED_NUMERIC", 72.0,
  "'a subcutaneous mass on his right buttock, which had gradually increased in size over"
  " 6 years' || 'The patient reported first palpating a peanut-sized subcutaneous mass"
  " that was non-tender on his right buttock 6 years earlier.'"),
 ("41323055","PMC12659415","SABR/surgery for metastatic EMC",
  "FULLTEXT_SILENT", None,
  "'A 39-year-old woman from Sri Lanka was diagnosed in 2019 with undifferentiated"
  " epitheliomorphic sarcoma of the right thigh.' -- no symptom-to-diagnosis interval."),
 ("39924782", None,"EMC mimicking mucinous ovarian cancer","UNRECOVERED", None,
  "no PMCID in the NCBI ID converter; no open-access full text; not attempted by a paywalled route"),
 ("37753118","PMC10519304","EMC identified in a traumatic fracture of the toe",
  "FULLTEXT_SILENT", None,
  "'complaints of the left 3rd toe pain and swelling that began after a traumatic impact to"
  " the foot while walking' -- acute onset, no duration; 'The erosive changes and osseous"
  " lesions were initially misdiagnosed as a fracture' -- NO time cost quantified."),
 ("35974707","PMC9527174","Immunosuppressive TME, pleural metastases",
  "FULLTEXT_SILENT", None,
  "'referred to our department with prickling chest pain and bilateral pleural effusions."
  " Three years earlier, she had undergone surgery and radiotherapy for EMCS of the right"
  " knee' -- treatment-to-metastasis interval, a DIFFERENT ESTIMAND; primary duration absent."),
 ("35494187","PMC9044308","HDR interstitial brachytherapy, ankle EMC",
  "FULLTEXT_STATED_NUMERIC", 360.0,
  "'An 87-year-old woman presented with a slow-growing tumor of the right ankle joint"
  " discovered 30 years ago. She refused to consult a doctor because she only experienced"
  " few symptoms. In 2015 ... she was diagnosed with EMC of the right ankle joint.'"),
 ("33075019", None,"EMC of the vulva confirmed by EWSR1 FISH","UNRECOVERED", None,
  "no PMCID; no open-access full text"),
 ("30967942","PMC6449903","O'Neill: vulval EMC misdiagnosed as Bartholin's cyst",
  "UNRECOVERED", None,
  "PMCID exists but get_full_text_article returned full_text=='' on TWO separate calls."
  " Abstract only: 'presented in 2011 with a swelling on the right labium majus. The tumour"
  " was initially misdiagnosed as a Bartholin's cyst and managed conservatively.'"
  " -- misdiagnosis asserted, interval NOT quantified in retrievable text."),
 ("28360467","PMC5351361","Curious case of EMC (axilla, lung metastases)",
  "FULLTEXT_STATED_QUALITATIVE", None,
  "'presented with complaints of right upper extremity pain while lifting heavy objects at"
  " work, from several months' (primary) || 'cough and hemoptysis for the past several"
  " weeks' (METASTATIC estimand, excluded)."),
 ("26504046", None,"Lockyer: EMC presenting as a plantar fibroma","UNRECOVERED", None,
  "no PMCID (Anticancer Res); no open-access full text. Misdiagnosis asserted in the"
  " abstract ('initially thought to be a plantar fibroma'); interval NOT quantified there."),
 ("25550031", None,"EMC of the thigh in a child","UNRECOVERED", None,"no PMCID"),
 ("24818862", None,"EMC arising in the femoral vein","UNRECOVERED", None,"no PMCID"),
 ("19894252", None,"FNA cytology of EMC","UNRECOVERED", None,"no PMCID"),
 ("7648738",  None,"Radionuclide imaging in EMC","UNRECOVERED", None,"no PMCID"),
 ("29886600", None,"Yue 2018, corpus callosum EMC (Chinese)","UNRECOVERED", None,
  "no PMCID AND no abstract in PubMed -- UNKNOWN by non-retrieval, already so graded by W04b"),
]

# W04b's own 2-of-2 probe: same conditioning (abstract silent), full text read.
W04B_PROBE = [
 ("26125202","Lubana 2015 (plantar)","FULLTEXT_STATED_NUMERIC",12.0),
 ("21941486","Mitchell 2011 (flank)","FULLTEXT_DERIVED_ONLY",6.0),
]

# W04b Table 2 stated primary-mass durations from ABSTRACTS (unchanged, preserved).
W04B_ABSTRACT_STATED = [36.0, 12.0, 6.0, 6.0, 6.0, 5.0, 2.0]   # n=7
W04B_N_CASE_REPORTS  = 26

def main():
    print("="*78)
    print("W04c -- full-text-denominator reporting rate, EMC symptom-to-diagnosis interval")
    print("Source: PubMed / PubMed Central (MCP). Nothing imputed. Unrecovered = UNKNOWN.")
    print("="*78)
    print("\n[0] INTERVAL IMPLEMENTATION CHECK (W04b fixed an inverted quantile here)")
    selftest()

    # ---- 1. per-paper outcomes for the 16
    print("[1] FULL-TEXT RETRIEVAL OUTCOMES FOR THE 16 ABSTRACT-SILENT CASE REPORTS")
    from collections import Counter
    c = Counter(r[3] for r in PROBE16)
    for k in ("FULLTEXT_STATED_NUMERIC","FULLTEXT_STATED_QUALITATIVE",
              "FULLTEXT_SILENT","UNRECOVERED"):
        print(f"  {k:<30}: {c[k]}")
    assert sum(c.values()) == 16
    recovered = [r for r in PROBE16 if r[3] != "UNRECOVERED"]
    print(f"  full texts actually READ                : {len(recovered)} / 16")
    print(f"  UNRECOVERED (UNKNOWN, not a negative)   : {c['UNRECOVERED']} / 16")

    # ---- 2. THE DELIVERABLE: full-text-denominator reporting rate
    print("\n[2] REPORTING RATE ON A FULL-TEXT DENOMINATOR  *** the deliverable ***")
    print("    denominator = EMC case reports that are ABSTRACT-SILENT and whose FULL TEXT")
    print("    I (or W04b) actually read. Conditional rate P(full text states | abstract silent).")
    mine_pos_strict = c["FULLTEXT_STATED_NUMERIC"] + c["FULLTEXT_STATED_QUALITATIVE"]
    n_mine = len(recovered)
    w04b_pos_strict = sum(1 for p in W04B_PROBE if p[2] == "FULLTEXT_STATED_NUMERIC")
    n_w04b = len(W04B_PROBE)
    for label, k, n in (
        ("this run only (W04c)",            mine_pos_strict, n_mine),
        ("W04b probe only (for reference)", w04b_pos_strict, n_w04b),
        ("COMBINED, strict (stated)",       mine_pos_strict + w04b_pos_strict, n_mine + n_w04b),
        ("COMBINED, lenient (+DERIVED)",    mine_pos_strict + n_w04b,          n_mine + n_w04b),
    ):
        lo, hi = clopper_pearson(k, n)
        print(f"  {label:<32}: {k}/{n} = {k/n:.3f}  [95% CP {lo:.3f}, {hi:.3f}]")
    lo, hi = clopper_pearson(mine_pos_strict + w04b_pos_strict, n_mine + n_w04b)
    print(f"  => W04b's 2/2 = 1.000 is NOT sustained: 1.0 lies ABOVE the upper limit {hi:.3f}.")
    print("     Abstracts do undercount (direction confirmed) but roughly HALF the")
    print("     abstract-silent reports are silent in full text too.")

    # ---- 3. corrected bound on the overall 26-report reporting rate
    print("\n[3] W04b TABLE 3, RECOMPUTED -- bound, not point estimate (no imputation)")
    known_pos = len(W04B_ABSTRACT_STATED) + w04b_pos_strict + mine_pos_strict
    still_unknown = W04B_N_CASE_REPORTS - (len(W04B_ABSTRACT_STATED) + n_w04b + n_mine)
    lo1, hi1 = clopper_pearson(known_pos, W04B_N_CASE_REPORTS)
    print(f"  case reports in W04b's set                       : {W04B_N_CASE_REPORTS}")
    print(f"  now KNOWN to state a primary-mass duration       : {known_pos}")
    print(f"  full text still never read -> status UNKNOWN     : {still_unknown}")
    print(f"  W04b lower bound (abstract level)                : 7/26 = {7/26:.3f}")
    print(f"  W04c lower bound (abstract + full text read)     : {known_pos}/26 ="
          f" {known_pos/26:.3f}  [95% CP {lo1:.3f}, {hi1:.3f}]")
    print(f"  interval of IGNORANCE (all unknowns -/+)         : "
          f"[{known_pos/26:.3f}, {(known_pos+still_unknown)/26:.3f}]")
    print("  The lower bound moved 0.269 -> "
          f"{known_pos/26:.3f}. It is still a LOWER BOUND.")

    # ---- 4. the case-report distribution, enlarged
    print("\n[4] CASE-REPORT DISTRIBUTION, ENLARGED  (*** NOT a delay estimate ***)")
    new_numeric = [r[4] for r in PROBE16 if r[4] is not None]
    stated = sorted(W04B_ABSTRACT_STATED + [12.0] + new_numeric)   # +Lubana full text
    derived = sorted(stated + [6.0])                               # +Mitchell DERIVED
    for label, v in (("stated durations only", stated),
                     ("+1 derived from dates", derived)):
        print(f"  {label:<24} n={len(v):>2}  median={st.median(v):6.1f} mo  "
              f"range={min(v):.0f}-{max(v):.0f} mo  values={[int(x) for x in v]}")
    print(f"  W04b had n=8, median 6.0, range 2-36.  Adding the two full-text values")
    print(f"  ({int(new_numeric[0])} mo and {int(new_numeric[1])} mo) moves the stated-only median "
          f"6.0 -> {st.median(stated):.1f} mo and")
    print("  extends the range 2-36 -> 2-360 mo. Both of the two longest durations in the")
    print("  whole corpus were INVISIBLE from abstracts. The abstract harvest truncated")
    print("  the right tail, which is the tail that matters for delay.")
    print("  DENOMINATOR OF THIS DISTRIBUTION = the case reports that CHOSE to state a")
    print("  duration. It is a distribution over PUBLICATION DECISIONS, not over patients,")
    print("  selected toward the unusual (buttock 40 cm, 30-year untreated ankle,")
    print("  nasopharynx, masticator space, plantar fascia, paediatric leg). It is NOT a")
    print("  diagnostic-delay estimate and must never be reported as one.")

    # ---- 5. system-side delay verdict
    print("\n[5] SYSTEM-SIDE DELAY (time the misreading cost) -- EXPLICIT VERDICT")
    print("  O'Neill  (30967942, vulval EMC as Bartholin's cyst) : UNRECOVERED (empty full text)")
    print("  toe EMC  (37753118, EMC as traumatic fracture)      : FULL TEXT READ -> NOT quantified")
    print("  Lockyer  (26504046, EMC as plantar fibroma)         : UNRECOVERED (no PMCID)")
    print("  hand EMC (41689087, EMC 'considered benign', unplanned excision elsewhere)")
    print("                                                      : FULL TEXT READ -> NOT quantified")
    print("  ankle EMC(35494187) quantifies 30 years, but attributes it to PATIENT-SIDE")
    print("           non-presentation ('She refused to consult a doctor'), NOT to a")
    print("           system misreading. It is not a system-side interval.")
    print("  VERDICT: 0 of 4 retrievable misdiagnosis narratives quantifies the time the")
    print("           misreading cost. NO system-side diagnostic-delay interval is")
    print("           recoverable from this literature. 2 of 4 remain UNRECOVERED, so this")
    print("           is a negative over what was READ, not proof of universal absence.")
    print("\nDone.")

if __name__ == "__main__":
    main()
```

---

## Limitations

- **Nine of sixteen full texts were never read.** 0.444 is measured on 9 abstract-silent case reports, not 25. Its 95% interval [0.137, 0.788] is wide, and the point estimate should not be quoted without it.
- **The full-text sample is not random — it is the open-access subset.** Every recovered paper had a PMC deposit; every unrecovered one did not. If open-access journals differ systematically in case-report length or narrative style (plausible: the recovered set skews toward long-form journals like *AJCR* and *J Contemp Brachytherapy*), 0.444 does not transfer to the closed-access half. This is a real, unquantified selection effect on the deliverable itself.
- **The 4/9 rate is conditional on abstract silence** and is not the unconditional reporting rate. The unconditional rate is bounded at [0.423, 0.808] and nothing here narrows that further without imputation, which the brief forbids and I did not perform.
- **One of the four positives is qualitative** (PMID 28360467, *"from several months"*). Counting it as a reporting event is a judgement; excluding it gives 3/9 = 0.333 [0.075, 0.700]. Both are stated so the reader can choose.
- **Table 4 remains a distribution over publication decisions.** n=10 does not make it a delay estimate, and the two new points make its selection toward the extraordinary *more* extreme, not less.
- **The system-side verdict is a negative over four narratives, two of them unread.** O'Neill (PMC6449903) is the most likely place such a number exists and it is UNKNOWN, not absent.
- **No clinical or causal claim is made or implied about delay and stage**, in either direction. Nothing here establishes that longer symptom duration causes worse presentation, or that it does not.
- **Transfer limit.** I inherited W04b's 26-report case set, its abstract-level coding, and its `SILENT_CASES` list without re-deriving them; if that set is incomplete, every denominator here inherits the gap. I did verify its two probe rows against my own reading and re-scored Mitchell 2011 from 2/2's numerator to DERIVED-only.
- **Repository note, not a claim about this lane:** the tracked corpus already cites PMC9044308 as `[FT]` (full text retrieved) for a brachytherapy dose and never recorded the 30-year duration in the same case paragraph. That is an observation about extraction coverage, not evidence of any error in the radiotherapy work.

---

## Stop condition

**Set:** full texts attempted for all 16 with per-paper outcomes recorded; a recomputed full-text-denominator reporting rate with an exact binomial interval; an explicit verdict on whether any source quantifies a system-side delay.

**Met — all three.** 16/16 attempted (7 read, 9 UNRECOVERED, each named individually in Table 1); reporting rate 4/9 = 0.444 [95% CP 0.137, 0.788] with the overall bound recomputed to [0.423, 0.808]; system-side verdict returned as an explicit negative over 4 narratives with the 2 unrecovered ones named. Neither an imputation nor a paywalled route was used.

---

## Tool-call and wall-clock count actually used

**16 tool calls** (9 Bash, 1 ToolSearch, 6 PubMed MCP). **Wall clock: 3 minutes 22 seconds** (`02:12:29Z` → `02:15:51Z`), well inside the ~40 min / ~40 call target.

---

## Next concrete action

**One successor, and it is narrow: resolve PMC6449903 (O'Neill 2019, vulval EMC) by a second open-access route.** The paper's PMC record exists and its `get_full_text_article` body came back empty on two separate calls in this session — that is a deposit or tool gap, **not** a paywall and not a denied route, so retrying it by a different legitimate open-access mechanism does not replay anything recorded as blocked. It is the single highest-value unread source in this lane: a *Molecular and Clinical Oncology* open-access paper whose title is *"A 5-year follow-up"*, whose abstract names diagnostic delay explicitly (*"patients may incur delays in diagnosis and treatment"*), which gives a presentation year of 2011 and describes a tumour *"initially misdiagnosed as a Bartholin's cyst and managed conservatively"* — the exact shape of a paper that would state, in its case section, how long the conservative management lasted. If it does, it is **the only system-side diagnostic-delay interval in the EMC literature**, and it is worth more than any further patient-side value. If it does not, this lane's negative is complete and should be closed rather than refilled again: the remaining 8 unrecovered full texts are all behind paywalls, and grinding the case-report distribution from n=10 to n=12 would add nothing but a longer list of publication decisions.

---

result: W04c converted W04b's 2/2 probe into a real measurement — full texts attempted for all 16 abstract-silent EMC case reports (7 read, 9 UNRECOVERED); the full-text-denominator reporting rate is 4/9 = 0.444 [95% CP 0.137, 0.788], so abstracts undercount but W04b's 1.000 is not sustained (1.0 exceeds the 0.788 upper limit); the overall case-report rate is bounded [0.423, 0.808]; two previously invisible durations (6 years, 30 years) extend the distribution to n=10, median 9.0 mo, range 2–360 mo while remaining a distribution over publication decisions; and the verdict on system-side delay is negative — 0 of 4 retrievable misdiagnosis narratives quantifies the time the misreading cost, with O'Neill and Lockyer UNRECOVERED.
