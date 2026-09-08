<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:18:29Z UTC
     agent id a4f864e849e1b43c7 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a4f864e849e1b43c7.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

- **Worker ID:** W04f — lane 4 refill, OPUS-CAPACITY-CAMPAIGN-20260908. Successor to W04e.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt, running under Claude Code 2.1.42. I did not observe the served model; no environment variable in this container names a model. The coordinator must extract the actual per-child runtime model from the transcript.
- **`date -u` at start:** `Tue Sep  8 03:11:06 UTC 2026` · **at end:** `Tue Sep  8 03:14:18 UTC 2026`
- **`git rev-parse HEAD` at start:** `98a0833f1ede2cf9cef13790388260567a32e868` · **at end:** `98a0833f1ede2cf9cef13790388260567a32e868` (unchanged; differs from the `92abbcb…` named as frozen in `COMMON-BRIEF.md`, as it did for W04d and W04e).
- **`git status --porcelain` at start and at end — byte-identical, eight untracked coordinator-collected reports, none of them mine:**
```
?? research/autonomy/opus-capacity-campaign-20260908/reports/W01g-transcriptome-wide-criterion.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W02f-fibro-ecm-decomposition.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W04e-delay-attribution-route.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W06f-coherent-share-readout.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W07f-emc-only-cohort-full-texts.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W09f-publications-false-absence-audit.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W12e-subprocess-env-residual.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W20g-published-denominator-consistency.md
```
All my execution was in `/tmp/claude-0/w04f/` (one file, `anchors.py`, 1847 bytes). **No write, move or delete anywhere under `/home/user/Rare-cancers`; no git write operation of any kind; `scripts/preflight.sh` not run.**
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** — literal output at end of run, abridged only by dropping the five long proxy lines (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy`), which match solely because they enumerate `api.anthropic.com` and carry no model identity. The start-of-run output was identical:

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

**Attribution (required by the PubMed tool's terms).** According to PubMed and PubMed Central, every article fact in this report was retrieved from PubMed. DOI links for every source I assert a fact about: PMID 30985717 [DOI](https://doi.org/10.1097/MD.0000000000015207); PMID 29657686 [DOI](https://doi.org/10.5001/omj.2018.29); PMID 26125202 [DOI](https://doi.org/10.12659/AJCR.894804); PMID 28638563 [DOI](https://doi.org/10.4317/jced.53888); PMID 38440485 [DOI](https://doi.org/10.1007/s12070-023-04271-6); PMID 27591381 [DOI](https://doi.org/10.1016/j.ijscr.2016.08.025); PMID 30325000 (no DOI in the PubMed record; `pii` `/article-medicale-tunisie.php?article=3343`); PMID 11917595 [DOI](https://doi.org/10.1159/000326743); PMID 40831041 [DOI](https://doi.org/10.12659/AJCR.947135); PMID 35494187 [DOI](https://doi.org/10.5114/jcb.2022.115161); PMID 21941486 [DOI](https://doi.org/10.1159/000331237); PMID 41635359 [DOI](https://doi.org/10.7759/cureus.100687); PMID 28360467 [DOI](https://doi.org/10.4103/0970-2113.201312); PMID 24713246 (no DOI in the ID-converter record).

**No clinical claim is made anywhere in this report.** Every interval below is a description of what a paper reported about one patient. Nothing here is a statement about prognosis, about harm from delay, or about what care should look like, and no recommendation is stated or implied. n=1 case reports support no rate, median or distribution *of patients*; the medians computed below are descriptive statistics **of a set of publication decisions**, computed only to test the stability of a committed repository figure.

---

## Question

**W04e showed that W04d's new minimum (1 month, PMID 41635359) is anchor-dependent, because the same patient's fatigue is reported at five to six months. Is that a property of one row or of the whole set — how many rows in W04d's duration set state more than one defensible interval, and what do the set's minimum, maximum, median and range become when one anchor convention is applied consistently?**

Open because no worker had ever enumerated the *full* set of intervals each source states. W04b and W04c each recorded **one** interval per paper (the one they pooled); W04d transcribed those and labelled the anchors; W04e found a second interval in exactly one paper and flagged, without measuring, that the property might generalise.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers` (read-only):

1. `git ls-files | rg -i "w04|anchor"` → the lane-4 reports `W04`, `W04b`, `W04c`, `W04d` are tracked; **`W04e` is not yet tracked** (it appears in `git status --porcelain` as `??`, and I read it from disk). The other `anchor` hits (`W17e-pub-atr-figure-anchoring.md`, `research/modalities/junction-anchor-convention-sensitivity.json`, `p1-anchor-convention.json`, `map_edit_anchors.py`, `S25-P1-ANCHOR.md`) are **splice-junction / figure-anchoring / map-edit** machinery — a different sense of "anchor" entirely, no overlap with clinical interval anchoring.
2. `rg -n "gastroesophageal|analgesics for several months|three months prior to his referral|five to six months" --glob '!.git' .` → the only clinical-interval hits in the whole tree are the two `five to six months` lines in `W04d:186` and `W04e:188,198`. **The phrases `analgesics for several months`, `three months prior to his referral` and the GORD/gastroesophageal-reflux misdirection sentence appear nowhere in the tracked tree** — the three second-anchor findings below are new to this repository.
3. `rg -n "27591381|28638563|21941486" --glob '!.git' -l .` → these PMIDs appear in `W04b`, `W04c`, `W04d` and in four unrelated probe/terminal-event JSONs; none of those JSONs carries a duration or anchor field.
4. Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, and reports `W04b`, `W04c`, `W04d`, `W04e`.

**Closed items confirmed not replayed.** I opened **no** route recorded as denied. I did not touch PMID 24703573 (Sunitinib 2014, three institutional 403 routes exhausted), Pazopanib, Trabectedin/RT 2018, Wagner 2020, CTARC 2022, the NR4A Perspective refusal, Hofvander/EGA, Brenca, GSE4303/GSE28866, the ICD-O paper, or the clinical registry. **I did not attempt PMID 19890812 under any label** — per W04e it is a standing UNRECOVERED / attribution-UNKNOWN entry and I left it exactly there. I did not re-derive W04c's harvest, did not re-run W04d's vocabulary widening, and did not enter lane 6's molecular-confirmation question. I used only PubMed MCP: no WebFetch, no WebSearch, no publisher route, no mirror, no aggregator, no paid API, no GPU. **No content-policy refusal occurred at any point in this run.**

---

## Method and inputs

**Committed inputs (read, not re-derived):** `research/autonomy/opus-capacity-campaign-20260908/reports/W04b-diagnostic-delay-interval.md`, `…/W04c-fulltext-duration-harvest.md`, `…/W04d-duration-set-stability.md`, plus the on-disk untracked `…/W04e-delay-attribution-route.md`, and the three briefs. Live cloud checkout at HEAD `98a0833f…`; I did **not** read the frozen corpus at `/tmp/claude-0/frozen-corpus/` this run.

**The set under test** = W04d's duration set: the ten stated values committed at `W04c:184`, plus the derived Mitchell value (`W04c:185`), plus W04d's addition PMID 41635359. PMID 19890812 (W04d's second addition) is **excluded by instruction** and carried as UNRECOVERED. PMIDs 28360467 (qualitative) and 24713246 (n=5 range) were included in the identifier guard for completeness but are not pooled by anyone and are not pooled here.

**Retrieval — PubMed MCP only, 4 calls:** `convert_article_ids` (guard, first), then `get_full_text_article` ×3 batches and `get_article_metadata` ×1.

**Identifier guard, RUN BEFORE any content retrieval — verbatim tool output:**

```
{"status":"ok","response-date":"2026-09-07 23:12:04","request":{"warnings":[],"format":"json","idtype":"pmid","ids":["30985717","29657686","26125202","28638563","38440485","27591381","30325000","11917595","40831041","35494187","21941486","41635359","28360467","24713246"],"tool":"pubmed-mcp-server","versions":"no","showaiid":"no"},"records":[{"pmcid":"PMC6485760","pmid":"30985717","doi":"10.1097/MD.0000000000015207","requested-id":"30985717"},{"pmcid":"PMC5889844","pmid":"29657686","doi":"10.5001/omj.2018.29","requested-id":"29657686"},{"pmcid":"PMC4492482","pmid":"26125202","doi":"10.12659/AJCR.894804","requested-id":"26125202"},{"pmcid":"PMC5474342","pmid":"28638563","doi":"10.4317/jced.53888","requested-id":"28638563"},{"pmcid":"PMC10908772","pmid":"38440485","doi":"10.1007/s12070-023-04271-6","requested-id":"38440485"},{"pmcid":"PMC5011171","pmid":"27591381","doi":"10.1016/j.ijscr.2016.08.025","requested-id":"27591381"},{"pmid":"30325000","requested-id":"30325000"},{"pmid":"11917595","requested-id":"11917595"},{"pmcid":"PMC12376927","pmid":"40831041","doi":"10.12659/AJCR.947135","requested-id":"40831041"},{"pmcid":"PMC9044308","pmid":"35494187","doi":"10.5114/jcb.2022.115161","requested-id":"35494187"},{"pmcid":"PMC3177793","pmid":"21941486","doi":"10.1159/000331237","requested-id":"21941486"},{"pmcid":"PMC12863220","pmid":"41635359","doi":"10.7759/cureus.100687","requested-id":"41635359"},{"pmcid":"PMC5351361","pmid":"28360467","doi":"10.4103/0970-2113.201312","requested-id":"28360467"},{"pmid":"24713246","requested-id":"24713246"}]}
```

**14/14 `requested-id` fields echo back exactly. Zero mismatches; nothing discarded.**

**Reachability actually achieved (PRIMARY):**

| Reachability class | n | PMIDs |
|---|---|---|
| PMCID exists **and** full-text body returned | 8 | 30985717, 26125202, 28638563, 27591381, 40831041\*, 35494187\*, 21941486, 41635359 |
| PMCID exists but `full_text` returned **`""`** → body UNRECOVERED, abstract only | 2 | 29657686 (PMC5889844), 38440485 (PMC10908772) |
| No PMCID → abstract only | 2 | 30325000, 11917595 |
| Excluded from the pooled set by every prior worker | 2 | 28360467 (qualitative), 24713246 (n=5 range) |

\* 40831041 and 35494187 were retrieved in full by W04c; to conserve budget I did **not** re-fetch them and instead used W04c's committed verbatim quotations, which the dispatch permits ("a verbatim sentence from a source you actually retrieved **or from a committed artifact**"). Every other quotation below comes from a body I retrieved in this run.

**One reconciliation, not a contradiction.** `W04c:105` records that the ID converter returned **neither** PMC10908772 nor PMC5011171 "for any of the 16 PMIDs" it queried. My guard returns both — for PMIDs **38440485** and **27591381**, which were *not* among W04c's 16 (they were abstract-stating papers, outside W04c's abstract-silent denominator). Both statements are true; the coordinator should not read them as a divergence.

**Computation.** One stdlib-only Python 3.11.15 script, `/tmp/claude-0/w04f/anchors.py`, returned inline below, run outside the repository. Medians, minima and maxima only — no confidence interval, deliberately.

---

## Result

### Finding 1 — every distinct interval each reachable source states, with its anchor, verbatim

Each row is the **complete** set of pre-diagnosis intervals I could find in the reachable text. Post-diagnosis intervals (follow-up, time to recurrence, survival) are excluded by definition and are not listed. All rows **PRIMARY** unless marked.

| PMID | Interval | Anchor (start → end) | Verbatim sentence | Source read |
|---|---|---|---|---|
| **30985717** | **36 mo** | mass noticed → presentation | *"This 11-year-old male had a **3-year history** of a slowly growing painless left leg mass, first noticed after trauma."* | full text |
| | *(no second interval)* | | | |
| **29657686** | **12 mo** | symptom onset → presentation | *"This case presented in the nasopharynx, an exceedingly unusual site for ESMC in a 60-year-old female with left-sided nasal obstruction and occasional epistaxis of **one-year duration**."* | abstract; **body UNRECOVERED** (`full_text` = `""`) |
| **26125202** | **12 mo** | mass noticed (= symptom onset; conflated in one clause) → presentation | *"A 58-year-old Jamaican woman presented at our hospital with complaints of a growth underneath the sole of her left foot **for 1 year**, with worsening pain."* | full text |
| **28638563** | **6 mo** | mass noticed → presentation | *"A 13-year-old male presented with a rapid enlarging painless diffuse mass located at the right midface and parotid region **over the last 6 months**."* | full text |
| | **3 mo** ← **second anchor, new to this repository** | **prior treatment → referral** | *"Past medical history included a previous surgical treatment attempt in his native country Honduras, **three months prior to his referral**."* | full text |
| **38440485** | **6 mo** | symptom onset → presentation | *"A 51-year-old diabetic, hypertensive female patient presented to our outpatient department with difficulty in chewing food for a **duration of 6 months**."* | abstract; **body UNRECOVERED** (`full_text` = `""`) |
| **27591381** | **6 mo** | symptom onset → presentation | *"During the last six months, he experienced intermittent hemoptysis without any other symptom."* | full text |
| | **~1 mo** ← **second anchor, new to this repository** | symptom escalation → self-obtained imaging | *"In the last month, the patient presented hemoptysis daily so he decided to get a CT scan of the chest."* | full text |
| | *(interval not stated)* | **prior treatment**, undated | *"An otolaryngologist explored the patient and initiated treatment for gastroesophageal reflux disease."* | full text |
| **30325000** | **5 mo** | symptom onset → presentation | *"We reported the case of a young patient of 18 years, accusing pelvic pain **for 5 months** with a poor general condition, an MRI was performed immediately…"* | abstract only (no PMCID) |
| **11917595** | **2 mo** | mass noticed **and** symptom onset, one clause | *"A 30-year-old female presented with left-sided chest pain and a hard lump in the breast of **two months' duration**."* | abstract only (no PMCID) |
| **40831041** | **72 mo** | mass noticed → presentation | *"The patient reported first palpating a peanut-sized subcutaneous mass that was non-tender on his right buttock **6 years earlier**."* | W04c committed artifact (`W04c:119`) |
| | **0.5 mo** | symptom escalation → presentation | *"…was accompanied by redness, swelling, and ulceration over the **previous 2 weeks**"* | W04c committed artifact |
| **35494187** | **360 mo** | mass discovered → **diagnosis** | *"An 87-year-old woman presented with a slow-growing tumor of the right ankle joint **discovered 30 years ago**. She refused to consult a doctor because she only experienced few symptoms. **In 2015**, … **she was diagnosed with EMC** of the right ankle joint based on biopsy results."* | W04c committed artifact (`W04c:120`); endpoint ambiguity of *"ago"* adjudicated by W04d in favour of 360 |
| **21941486** (DERIVED) | **~6 mo** | first presentation → pathological diagnosis | *"…presented to an outside institution in **April 2009** with a painful, enlarging left flank mass. … Pathological review of a biopsy in **October 2009** characterized the lesion as high grade (FNCLCC 3/3)…"* | full text |
| | **~5 mo** (DERIVED) | first presentation → first cross-sectional imaging | *"He was treated with oral analgesics for several months, before computed tomography of the abdomen in **September 2009** revealed a 6.2 × 4.5 cm solid mass…"* | full text |
| | *(symptom onset never dated → first-symptom anchor is **UNKNOWN** for this patient)* | | | |
| **41635359** | **1 mo** | mass noticed → presentation | *"The palpable non-tender abdominal mass had been present for **one month**."* | full text (re-verified this run) |
| | **5–6 mo** | first symptom (fatigue) → presentation | *"The patient reported **five to six months** of significant fatigue."* | full text (re-verified this run) |

**Not pooled by anyone, listed for completeness:** 28360467 states *"right upper extremity pain while lifting heavy objects at work, from several months"* and *"cough and hemoptysis for the past several weeks"* — two qualitative intervals, no number; 24713246 states a bare 3–12 month range over n=5 with an unstated non-missing denominator.

### Finding 2 — how many rows carry the anchor property

| | n | Rows |
|---|---|---|
| Rows in the pooled set (10 stated + 1 derived + W04d's 41635359) | **12** | — |
| **Rows stating ≥2 distinct pre-diagnosis intervals** | **5 / 12 (42%)** | 28638563, 27591381, 40831041, 21941486, 41635359 |
| Rows stating exactly one interval | 7 / 12 | 30985717, 29657686, 26125202, 38440485, 30325000, 11917595, 35494187 |
| Rows where the **committed value would change** under a different defensible anchor | **1 / 12 (8%)** | **41635359 only** (1 → 5–6) |
| Rows where a second interval exists but is a *different estimand* (escalation, prior treatment, imaging step) rather than a competing reading of the same estimand | 4 / 12 | 28638563, 27591381, 40831041, 21941486 |

**This is the load-bearing distinction, and it is the answer to the dispatch's "say so plainly if the anchor changes nothing."** W04e's finding **does not generalise as a value-changing property**. Two out of five multi-interval rows are 40831041 and 27591381, where the mass/first symptom *is* the earliest event, so the first-symptom anchor returns the committed value unchanged (72 and 6). 28638563's second interval is a prior-treatment date, a different estimand. 21941486's two intervals are both inside the presentation→diagnosis segment. **PMID 41635359 remains the only row in the entire set where two anchors give two different numbers for the same estimand** — because it is the only paper reporting a systemic symptom (fatigue) that predates the mass.

### Finding 3 — the set under each convention applied consistently

Conventions defined in advance. A row with no interval on a given anchor is **UNKNOWN and dropped**, never imputed.

| Convention | Definition | n | Median (mo) | Min | Max | Range |
|---|---|---|---|---|---|---|
| **Committed, mixed anchors** (`W04c:184`) | as published | 10 | **9.0** | 2 | 360 | 2–360 |
| **Committed + 41635359, mixed anchors** (`W04d`) | as published | 11 | **6.0** | **1** | 360 | **1–360** |
| **A — mass noticed → presentation**, consistently | 4 symptom-only rows become UNKNOWN | **7** | **12.0** | **1** | 360 | 1–360 |
| **B — first stated symptom → presentation**, consistently | 21941486 UNKNOWN (onset never dated); 41635359 = 5 | **11** | **6.0** | **2** | 360 | **2–360** |
| **B′ — same, 41635359 = 6** | upper reading of "five to six months" | 11 | **6.0** | **2** | 360 | 2–360 |
| **C — presentation → pathological diagnosis** | only one source states/derives it | **1** | 6.0 | 6 | 6 | — |
| **D — prior treatment → referral** | only one source states it | **1** | 3.0 | 3 | 3 | — |
| *Reference:* committed 10 rows scored under **B** | | 10 | **9.0** | 2 | 360 | 2–360 |
| *Reference:* committed 10 rows scored under **A** | 4 rows dropped as UNKNOWN | **6** | **24.0** | 2 | 360 | 2–360 |

**Read the table this way — three separate results:**

1. **The anchor does not change the committed ten values at all.** Scored under B, the ten committed rows return **exactly** the committed multiset `2,5,6,6,6,12,12,36,72,360`, median 9.0, range 2–360. Each of those ten papers states **one** pre-diagnosis interval, so W04d's Finding-2 anchor *labels* differ across the set while the *numbers* do not. The anchor mixing W04d identified is real as a labelling heterogeneity and **numerically inert for the committed figure**. That is the plain "it changes nothing" answer, and it applies to the median and the maximum.
2. **The anchor does change the minimum, and only the minimum.** W04d's new bound of 1 month exists under A and vanishes under B, where the minimum stays at the committed 2 months. This is exactly W04e's caveat, now measured: it is a **one-row, one-statistic** effect.
3. **The anchor changes set membership far more than it changes values, and that is the larger instability.** Applying A strictly — the anchor W04d names for the majority of its rows — makes four of the ten committed rows UNKNOWN (29657686, 38440485, 27591381, 30325000 state a symptom duration and never say when a mass was noticed). n falls 10 → 6 and the median moves **9.0 → 24.0 months**, a 167% shift, dwarfing the 33% shift W04d found by adding a paper. **The committed set is only n=10 because it pools two anchors; no single consistently-applied anchor supports a set larger than 11, and the strictest one supports 6.**

### Finding 4 — committed downstream statements that change

| Committed statement | Status under this run | Label |
|---|---|---|
| `W04c:184` **n=10, median 9.0, range 2–360** | **UNCHANGED under B**; under A the set is n=6, median 24.0. The number is not wrong; its *estimand* is "whatever interval each paper chose to report" | PRIMARY |
| `W04d` **"the widening extends the range at *both* ends, not only the tail"** | **HOLDS ONLY UNDER A.** Under a consistent first-symptom convention the minimum stays 2 and only the tail is extended. Needs the anchor stated inline | PRIMARY |
| `W04d` Table row **"+41635359 only … n=11 … 6.0 … 1–360"** | **Median 6.0 is anchor-invariant** (B and B′ both give 6.0). **Only the `1` in the range is anchor-dependent**; it should read `1–360 (mass-noticed anchor) / 2–360 (first-symptom anchor)` | PRIMARY |
| `W04d`'s headline disagreement — **"moves the headline median from 9.0 months to 6.0 months, a 33% shift … the median is not stable to a single admissible addition"** | **SURVIVES INTACT under every convention tested.** This is W04d's sharpest claim and the anchor does not touch it | PRIMARY |
| `W04d` Finding 2, **"three distinct anchor pairs are pooled in the committed n=10 set"** | **CONFIRMED and refined**: the pooling is real, and I add that it is *numerically inert* for the committed values but *load-bearing for set membership* (n=10 → 6 under A) | PRIMARY |
| `W04c:206` **"no source quantifies a system-side diagnostic delay"** | **W04e already retired the general form.** I add a second, independent pressure point: **PMID 21941486's full text derives a system-side segment** — presentation at an outside institution **April 2009**, oral analgesics *"for several months"*, CT **September 2009**, diagnosis **October 2009** — i.e. ~5 months to first imaging and ~6 months to diagnosis, spent under clinician-directed treatment. It is **DERIVED from dates, not stated as a delay**, so the wording *"no source **states** a system-side interval"* survives; *"quantifies"* does not | SECONDARY (derived) |
| `W04c:196–207` **"zero of four retrievable EMC misdiagnosis narratives states the time the misreading cost"** | **STANDS**, and its denominator is now visibly incomplete: **PMID 27591381 is a fifth misattribution narrative** — *"An otolaryngologist explored the patient and initiated treatment for gastroesophageal reflux disease"* during six months of hemoptysis — and it too **states no interval for the misattribution**. The verdict's substance is reinforced; only its denominator of four is understated | PRIMARY |
| `W04b`/`W04c` framing: **a distribution over publication decisions, not over patients**; **any claim that diagnostic delay drives EMC presentation stage is unsupported in either direction** | **UNCHANGED and strengthened.** A set whose n halves and whose median more than doubles under a stricter anchor is not a patient distribution | PRIMARY |
| `W04c:185` / `W04b:178–179,191,482` — the two-live-medians divergence W04d flagged | **Untouched by this run**; still awaiting the coordinator-side reconciliation W04d and W04e both requested | — |

---

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Claude Code 2.1.42, Python 3.11.15, repository `/home/user/Rare-cancers` at HEAD `98a0833f…` (read-only to me), all execution in `/tmp/claude-0/w04f/`.

| # | Command / call | Exit / status | Key verbatim output |
|---|---|---|---|
| 1 | `date -u; git rev-parse HEAD; git status --porcelain; env \| grep …` | 0 | start `Tue Sep  8 03:11:06 UTC 2026`; HEAD `98a0833f…`; 8 untracked coordinator files |
| 2 | `ls` campaign dir + `reports/` | 0 | `W04e-delay-attribution-route.md` present |
| 3 | `cat COMMON-BRIEF.md CLOSED-WORK.md CORPUS-CONTEXT.md` | 0 | read in full |
| 4 | `sed -n` over `W04b`, `W04c`, `W04d`, `W04e` | 0 | tables and verdicts read verbatim |
| 5 | `mcp__PubMed__convert_article_ids` (guard, **before** any content call) | `"status":"ok"` | quoted in full above; **14/14 match, 0 discarded** |
| 6 | `mcp__PubMed__get_full_text_article(["PMC6485760","PMC5889844","PMC4492482"])` | `"count":3` | PMC5889844 `full_text` = `""`; other two bodies retrieved |
| 7 | `mcp__PubMed__get_full_text_article(["PMC5474342","PMC10908772","PMC5011171"])` | `"count":3` | PMC10908772 `full_text` = `""`; the Honduras and GORD sentences retrieved |
| 8 | `mcp__PubMed__get_full_text_article(["PMC3177793","PMC12863220"])` | `"count":2` | Mitchell date chain and the fatigue sentence retrieved |
| 9 | `mcp__PubMed__get_article_metadata(["30325000","11917595"])` | `"count":2` | both abstracts retrieved; 30325000 carries no DOI |
| 10 | `python3 /tmp/claude-0/w04f/anchors.py` | **0** | full output below |
| 11 | `rg`/`git ls-files` novelty greps | 0 | see Prior-work check |
| 12 | `date -u; git rev-parse HEAD; git status --porcelain; ls -la /tmp/claude-0/w04f` | 0 | end `Tue Sep  8 03:14:18 UTC 2026`; HEAD unchanged; status byte-identical; scratch holds only `anchors.py` |

Script authored by me, returned inline, **not written into the tree**:

```python
#!/usr/bin/env python3
import statistics as s
def d(name, v):
    v=sorted(v)
    print(f"{name:56s} n={len(v):3d} median={s.median(v):7.1f} min={min(v):6.1f} max={max(v):6.1f}")
    print(f"{'':56s} values={v}")

# Convention A: mass-noticed -> presentation. Rows stating no mass-noticing interval are UNKNOWN (dropped).
A = {'30985717':36,'26125202':12,'28638563':6,'11917595':2,'40831041':72,'35494187':360,'41635359':1}
# Convention B: first stated symptom of any kind -> presentation. 21941486 UNKNOWN (onset never dated).
B = {'30985717':36,'29657686':12,'26125202':12,'28638563':6,'38440485':6,'27591381':6,
     '30325000':5,'11917595':2,'40831041':72,'35494187':360,'41635359':5}
B6 = dict(B); B6['41635359']=6          # upper reading of "five to six months"
# Convention C: presentation -> pathological diagnosis
C = {'21941486':6}
# Convention D: prior treatment -> referral/presentation
D = {'28638563':3}
# Committed mixed set as W04d published it (10 committed values + 41635359 at 1 mo)
MIX = [2,5,6,6,6,12,12,36,72,360,1]
COMMITTED10 = [2,5,6,6,6,12,12,36,72,360]

print("== committed, mixed anchors (as published) ==")
d("W04c:184 committed n=10 (headline)", COMMITTED10)
d("W04d n=11 (+41635359 at 1 mo, mixed anchors)", MIX)
print("\n== one convention applied consistently ==")
d("A  mass-noticed -> presentation", list(A.values()))
d("B  first symptom -> presentation (fatigue=5)", list(B.values()))
d("B' first symptom -> presentation (fatigue=6)", list(B6.values()))
d("C  presentation -> pathological diagnosis", list(C.values()))
d("D  prior treatment -> referral", list(D.values()))
print("\n== committed 10 rows scored under A and under B ==")
d("committed 10 under B (all rows have a B value)", [B[k] for k in B if k!='41635359'])
d("committed 10 under A (4 rows UNKNOWN, dropped)", [A[k] for k in A if k!='41635359'])
```

Verbatim output, **exit code 0**:

```
== committed, mixed anchors (as published) ==
W04c:184 committed n=10 (headline)                       n= 10 median=    9.0 min=   2.0 max= 360.0
                                                         values=[2, 5, 6, 6, 6, 12, 12, 36, 72, 360]
W04d n=11 (+41635359 at 1 mo, mixed anchors)             n= 11 median=    6.0 min=   1.0 max= 360.0
                                                         values=[1, 2, 5, 6, 6, 6, 12, 12, 36, 72, 360]

== one convention applied consistently ==
A  mass-noticed -> presentation                          n=  7 median=   12.0 min=   1.0 max= 360.0
                                                         values=[1, 2, 6, 12, 36, 72, 360]
B  first symptom -> presentation (fatigue=5)             n= 11 median=    6.0 min=   2.0 max= 360.0
                                                         values=[2, 5, 5, 6, 6, 6, 12, 12, 36, 72, 360]
B' first symptom -> presentation (fatigue=6)             n= 11 median=    6.0 min=   2.0 max= 360.0
                                                         values=[2, 5, 6, 6, 6, 6, 12, 12, 36, 72, 360]
C  presentation -> pathological diagnosis                n=  1 median=    6.0 min=   6.0 max=   6.0
                                                         values=[6]
D  prior treatment -> referral                           n=  1 median=    3.0 min=   3.0 max=   3.0
                                                         values=[3]

== committed 10 rows scored under A and under B ==
committed 10 under B (all rows have a B value)           n= 10 median=    9.0 min=   2.0 max= 360.0
                                                         values=[2, 5, 6, 6, 6, 12, 12, 36, 72, 360]
committed 10 under A (4 rows UNKNOWN, dropped)           n=  6 median=   24.0 min=   2.0 max= 360.0
                                                         values=[2, 6, 12, 36, 72, 360]
exit=0
```

**PROPOSED (NOT RUN), and deliberately not run:** any route to PMID 19890812 (standing UNRECOVERED, excluded by instruction); a second retrieval route for the two PMC bodies that returned `""` (PMC5889844, PMC10908772) — this is a deposit- or tool-side gap and I recorded it rather than probing further, since my dispatch caps retrieval at PubMed MCP and I had the abstracts I needed; re-fetching PMC12376927 and PMC9044308 to re-enumerate their intervals independently of W04c; any full text of the 9 UNRECOVERED W04c case reports; any re-derivation of W04c's harvest or W04d's widening.

---

## Limitations

- **Two of the twelve rows were scored from abstracts alone because their PMC bodies came back empty** (29657686, 38440485), and two more have no PMCID at all (30325000, 11917595). For those four, a second interval could exist in unread text. Their single-interval status is **a lower bound on interval count, not a negative** — my 5/12 multi-anchor count is therefore itself a **lower bound**.
- **Two rows (40831041, 35494187) were not re-retrieved this run**; their intervals are taken from W04c's committed verbatim transcription, which the dispatch permits but which means I did not independently search those bodies for a third interval.
- **"Defensible anchor" is my judgement.** I counted a second interval as an alternative anchor only when it describes a pre-diagnosis event in the same patient. A different adjudicator could, for instance, treat 40831041's two-week ulceration as the presenting-complaint anchor and move that row from 72 to 0.5, which would change the maximum. I flagged the interval and did not adopt that convention.
- **Convention A's n=6/n=7 sets are small enough that their medians are near-meaningless as statistics**; I report them to show the *magnitude of the membership effect*, not as an estimate of anything.
- **No confidence interval is computed, deliberately** — over a set of publication decisions with heterogeneous estimands, a CI would imply a sampling model that does not exist.
- **n=1 throughout.** Every value is one patient in one case report. Nothing here is a rate, a distribution over patients, a median delay, or a comparison. I pooled nothing beyond the descriptive recomputation of an already-committed repository figure.
- **No clinical inference of any kind.** No prognosis, no claim that any delay caused any harm, no statement about what care should look like, no recommendation, explicit or implied. There is no wet lab and nothing here bears on EMC efficacy, safety or clinical readiness.
- **Model identity is self-report only.** My read HEAD (`98a0833f…`) differs from the `92abbcb…` declared frozen in `COMMON-BRIEF.md`, as it did for W04d and W04e; it did not move during my run.

---

## Stop condition

**Set up front, before retrieval:** *Return the moment (a) the identifier guard has run on the whole set and its verbatim output is recorded, (b) every reachable source's complete set of stated pre-diagnosis intervals is enumerated with anchor and verbatim quote, (c) the count of multi-anchor rows and the per-convention min/max/median/range are computed from an actually-executed script, and (d) the affected committed downstream statements are listed.*

**MET, all four parts.** (a) 14/14 identifier match, zero discarded, output quoted in full; (b) 12 pooled rows plus 2 excluded rows enumerated, 8 bodies read this run, 2 bodies UNRECOVERED, 2 abstract-only, 2 taken from W04c's committed quotes; (c) **5 of 12 rows carry ≥2 intervals but only 1 of 12 changes value under a different anchor**, and the six per-convention set statistics are computed with exit code 0; (d) nine committed statements assessed, three of which need wording changes. Returned on satisfaction, not padded.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 13** (7 Bash, 1 ToolSearch, 4 PubMed MCP, plus the final accounting Bash), against a ~40-call target.
- **Wall clock: `03:11:06Z` → `03:14:18Z` ≈ 3 minutes 12 seconds**, against a ~40-minute target. Short because the question resolved cleanly once the twelve sources' full interval sets were in hand.

---

## Next concrete action

**One successor, finite, coordinator-side, needing no new retrieval: apply three narrow wording corrections and one denominator correction to the committed lane-4 reports, then close the anchor question.** Specifically — (a) annotate W04d's `+41635359` row so the range reads `1–360 (mass-noticed anchor) / 2–360 (first-symptom anchor)` and its "extends the range at both ends" sentence carries its anchor inline, since the median 6.0 and W04d's 33%-shift finding are anchor-invariant and must not be softened along with it; (b) add to W04d's Finding 2 the measured result that the anchor mixing is **numerically inert for the ten committed values but halves n under a consistently-applied mass-noticed anchor (10 → 6, median 9.0 → 24.0)** — that is the bigger instability and it is currently unrecorded; (c) correct W04c's misdiagnosis-narrative denominator from four to **five**, adding PMID 27591381 (*"An otolaryngologist … initiated treatment for gastroesophageal reflux disease"*), noting it too states no interval, so the verdict's substance is unchanged; (d) record that PMID 21941486's dated chain (April 2009 presentation → analgesics → September 2009 CT → October 2009 diagnosis) is a **DERIVED** system-side segment, so W04c's negative should read *"no source **states** a system-side interval"* rather than *"quantifies"*.

**And an explicit non-successor:** there is no further *retrieval* successor worth funding in this lane. The two PMC bodies that returned `""` are a tool- or deposit-side gap rather than a paywall, but recovering them could at most add one more single-patient interval to a set that is already known not to be a patient distribution; PMID 19890812 remains a standing UNRECOVERED / attribution-UNKNOWN entry and must not be re-attempted under a new label. **The anchor question itself is now closed: it changes the minimum of one row and the membership of the set, and it changes neither the committed median nor W04d's instability finding.**
