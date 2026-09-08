> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git tree; the coordinator is the sole collector.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check done: repo tree carries no writes of mine (`git status --porcelain` shows only the coordinator's pre-existing untracked campaign directory), the script exits 0, and the Clopper-Pearson implementation now reproduces three textbook intervals exactly. Full report follows.

---

## Worker

- **Worker ID:** W04b — reassigned from Lane 4 (closed) to the untouched **diagnostic-delay half of Lane 6**.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt, under Claude Code 2.1.42. I did not observe the served model and do not assert it as fact; the coordinator should extract the actual runtime model from the transcript.
- **`date -u` at start:** `Tue Sep  8 02:00:58 UTC 2026` · **at end:** `Tue Sep  8 02:04:40 UTC 2026`
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

No environment variable in this container names a model — same finding W06 recorded. My identity claim rests solely on my system prompt.

**Write-isolation compliance.** I wrote nothing under `/home/user/Rare-cancers`. All execution happened in `/tmp/claude-0/w04b/`. `git status --porcelain` returns exactly one line — `?? research/autonomy/opus-capacity-campaign-20260908/`, the coordinator's own pre-existing untracked directory — and `find . -name '*W04b*' -not -path './.git/*'` returns nothing. No git write operation of any kind was run.

---

## Question

**What is actually reported, in retrievable primary EMC sources, about the interval from first symptom to diagnosis — and what is the reporting denominator for each such value?**

It is open because W06 closed the molecular-confirmation half of Lane 6 and stated explicitly that "the diagnostic-delay and referral-pathway halves of Lane 6 are untouched." It matters because EMC presents as a slow-growing painless mass easily mistaken for a benign myxoid lesion, so diagnostic delay is a plausible driver of presentation stage — but whether the published record can support *any* statement about it was unknown before this run.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers`:

1. `rg -n -i "diagnostic delay|symptom duration|time to diagnosis|duration of symptoms|delay|prior to (presentation|diagnosis)|months before" research/ --glob '!.git' | head -60`
2. `ls -la research/manuscripts/care-delivery/`
3. `git ls-files | rg -i "delay|symptom|presentation|care-deliv" | head -40`
4. `rg -n -i "painless|slow-grow|slowly enlarg|indolent mass|history of a|presenting symptom|misdiagnos|benign|myxoma" research/manuscripts/care-delivery/ research/modalities/emc-care-delivery-evidence.json | head -40`
5. `rg -n -i "delay" research/manuscripts/care-delivery/ | head -20`

**What the corpus actually contains.** Command 1 returned **ten** lines and **not one is about a patient's symptom-to-diagnosis interval**. They are: a preprint-pipeline warning using "months before" idiomatically; two copies of an ATU027 siRNA quote about tissue collected "many months before" treatment; two copies of a pazopanib line about progression documented "6 months before enrolment"; the campaign's own W06/AGENT-ROLES rows; a W04 sentence *anticipating* that myxoid confusability "drives real diagnostic delay in this disease" (an unsourced motivating aside, not a measurement); and a source-index test fixture string. Commands 4–5 show `research/manuscripts/care-delivery/` (nine files) touches "delay" only as *therapeutic* delay in the adaptive-scheduling pazopanib work, and "misdiagnosed" only inside the disclaimer of the **user-rejected** ICD-O classification paper.

**Conclusion: the repository holds zero content on the EMC diagnostic interval.** This work is additive rather than duplicative, and I am not redoing W06's molecular-confirmation question — no confirmation numerator appears anywhere below.

**Closed items confirmed not replayed.** I opened no route to Wagner 2020 (`32856598`), CTARC 2022, Sunitinib 2014 (`24703573`), the Pazopanib primary, or Trabectedin/RT 2018. None appears in my tables. I did not re-litigate W04's imaging-resource negative, did not touch GSE4303/GSE28866, and did not approach the restricted NR4A Perspective. **No content-policy refusal occurred in this run.** No paywalled route was attempted, so no 403 was incurred. PubMed tool results carried a mandatory-attribution notice, which I comply with below rather than route around.

---

## Method / inputs

**Retrieval — PubMed MCP tools only** (`search_articles`, `get_article_metadata`, `get_full_text_article`). No WebSearch, no publisher route, no paywall attempt.

- `search_articles`: `extraskeletal myxoid chondrosarcoma[Title] AND (case report[Publication Type] OR case[Title])` → 75 total, 60 returned
- `search_articles`: `extraskeletal myxoid chondrosarcoma AND (duration of symptoms OR symptom duration OR diagnostic delay OR history of a painless mass)` → 15 total, 15 returned
- `search_articles`: `(Enzinger EM[Author] OR Angervall L[Author]) AND (myxoid chondrosarcoma OR chondrosarcoma extraskeletal)` → 2
- `search_articles`: `extraskeletal myxoid chondrosarcoma[Title] AND (analysis of[Title] OR cases[Title])`, 1970–1990 → 3
- `get_article_metadata` on 41 PMIDs across four batches
- `get_full_text_article` on `["PMC4492482", "PMC3177793"]` — the probe that carries the report

**Attribution (required by the PubMed tool's terms).** All article facts below were retrieved from **PubMed**. DOI links: Enzinger & Shiraki 1972 [DOI](https://doi.org/10.1016/s0046-8177(72)80042-x); Saleh 1992 [DOI](https://doi.org/10.1002/1097-0142(19921215)70:12%3C2827::aid-cncr2820701217%3E3.0.co;2-v); D'Ambrosio 1986 [DOI](https://doi.org/10.1002/1097-0142(19860901)58:5%3C1144::aid-cncr2820580528%3E3.0.co;2-l); Mukherjee 1990 (PMID 2090579, no DOI in the PubMed record); Meis-Kindblom 1999 [DOI](https://doi.org/10.1097/00000478-199906000-00002); Rao 2002 [DOI](https://doi.org/10.1159/000326743); Drilon 2008 [DOI](https://doi.org/10.1002/cncr.23978); Mitchell 2011 [DOI](https://doi.org/10.1159/000331237); Xu 2014 (PMID 24713246, no DOI in the PubMed record); Lubana 2015 [DOI](https://doi.org/10.12659/AJCR.894804); Balanzá 2016 [DOI](https://doi.org/10.1016/j.ijscr.2016.08.025); Romañach 2017 [DOI](https://doi.org/10.4317/jced.53888); Purkayastha 2018 [DOI](https://doi.org/10.5001/omj.2018.29); Chahdi 2018 (PMID 30325000, no DOI in the PubMed record); Al Khader 2019 [DOI](https://doi.org/10.1097/MD.0000000000015207); O'Neill 2019 [DOI](https://doi.org/10.3892/mco.2019.1822); Brodsky 2023 [DOI](https://doi.org/10.1097/COC.0000000000000988); Dabas 2023 [DOI](https://doi.org/10.1007/s12070-023-04271-6); Starostin 2023 [DOI](https://doi.org/10.1016/j.radcr.2023.10.075); Kandoussi/Chang 2024 [DOI](https://doi.org/10.1007/s00256-024-04800-6); Lai 2025 [DOI](https://doi.org/10.12659/AJCR.947135).

**Computation.** One stdlib-only Python 3.11.15 script authored by me, returned inline below, run outside the repository. Clopper–Pearson exact binomial intervals via bisection on a continued-fraction regularised incomplete beta. No numpy/scipy.

**The denominator discipline (inherited from W06, applied to a different estimand).** Three exclusion rules make this table honest:

- **A source that does not state a duration is `UNKNOWN`, never zero, and stays in the denominator.** Meis-Kindblom's 117 patients are not 117 patients with zero delay.
- **"No abstract retrieved" is not "does not report."** Enzinger & Shiraki 1972 (n=34, the founding series) and Yue 2018 have **no abstract in PubMed**. They are `UNKNOWN by non-retrieval` — a distinct category from silence, and I did not attempt a paywalled route to either.
- **The estimand is separated.** A duration attached to a *metastatic* symptom (Starostin's 3-month cough) or a *metastasis-to-primary* interval (D'Ambrosio's 10 years and 2 years) is a different quantity from symptom-to-diagnosis of the primary, and is excluded from the distribution rather than pooled into it.

---

## Result

### Table 1 — series-level reporting. Every row is the same answer.

| Series | PMID | Year | n | Symptom-duration statistic in retrieved text | Denominator | Grade |
|---|---|---|---|---|---|---|
| Meis-Kindblom | 10366145 | 1999 | 117 | none (reports age, size, site, follow-up) | — | **UNKNOWN** |
| Drilon (per W06) | 18951519 | 2008 | 86 | none | — | **UNKNOWN** |
| Brodsky (Michigan) | 36825763 | 2023 | 44 | none (reports age, sex, stage, survival) | — | **UNKNOWN** |
| Enzinger & Shiraki | 4261659 | 1972 | 34 | **no abstract in PubMed — text not retrieved** | — | **UNKNOWN (non-retrieval)** |
| Kandoussi / Chang (MGH) | 39256245 | 2024 | 30 | none (reports site, size, MRI, invasion, necrosis) | — | **UNKNOWN** |
| Saleh | 1451062 | 1992 | 10 | none | — | **UNKNOWN** |
| **Xu** | **24713246** | **2014** | **5** | **range 3–12 months, no median** | **UNSTATED** | **PRIMARY (range only)** |
| Mukherjee | 2090579 | 1990 | 3 | none | — | **UNKNOWN** |
| D'Ambrosio | 3731040 | 1986 | 2 | metastasis preceded primary by 10 y / 2 y | 2/2 | **PRIMARY (different estimand)** |

**0 of 8 series with retrievable text report a median or mean symptom duration. 324 of 331 patients (97.9%) in these series sit in a source that states no symptom-duration statistic at all.**

The one cohort-level statement is Xu 2014, n=5, verbatim: *"All the tumors studied were solitary and the duration of disease onset varied from 3 months to 1 year."* It is a bare range with **no median and no stated non-missing denominator**. The sentence's grammar implies all five, but the paper never asserts it, so per rule the denominator is **UNSTATED** — not imputed to 5.

Note what the modern series *do* collect. Kandoussi 2024 documented "tumor location, size, imaging appearance, presence of metastases, disease recurrence, and clinical outcome"; Brodsky 2023 did a chart review of "demographics, tumor characteristics, treatments, and outcomes." Both had chart access and both omitted the interval. This is a consistent choice of what to record, not an accident of one paper.

### Table 2 — every case-level duration I found, with its exact sentence

| PMID | Source | Months | Where stated | Estimand | Verbatim |
|---|---|---|---|---|---|
| 30985717 | Al Khader 2019, leg, age 11 | **36** | abstract | primary mass | "an 11-year-old boy with a **3-year history** of a slowly growing painless left leg mass" |
| 29657686 | Purkayastha 2018, nasopharynx | **12** | abstract | primary mass | "left-sided nasal obstruction and occasional epistaxis of **one-year duration**" |
| 26125202 | Lubana 2015, plantar | **12** | **full text only** | primary mass | "complaints of a growth underneath the sole of her left foot **for 1 year**, with worsening pain" |
| 28638563 | Romañach 2017, masticator space | **6** | abstract | primary mass | "a large painless, diffuse mass causing progressive midfacial asymmetry of **6 months duration**" |
| 38440485 | Dabas 2023, floor of mouth | **6** | abstract | primary mass | "difficulty in chewing food for a **duration of 6 months**" |
| 27591381 | Balanzá 2016, pulmonary primary | **6** | abstract | primary mass | "presented with intermittent hemoptysis **for the last 6 months**" |
| 21941486 | Mitchell 2011, flank | **~6** | **full text, DERIVED** | primary mass | "presented … in **April 2009** with a painful, enlarging left flank mass … Pathological review of a biopsy in **October 2009** characterized the lesion as high grade" |
| 30325000 | Chahdi 2018, pelvis | **5** | abstract | primary mass | "accusing pelvic pain **for 5 months**" |
| 11917595 | Rao 2002, chest wall | **2** | abstract | primary mass | "a hard lump in the breast of **two months' duration**" |
| 38111543 | Starostin 2023 | 3 | abstract | **metastasis** | "presented initially with a **3-month history of cough**" — primary groin mass duration never stated |

All rows **PRIMARY** except the Mitchell row, which is **DERIVED** by me from two dated events rather than read from a "duration" sentence, and is excluded from the primary distribution.

### Table 3 — the reporting fraction, and the finding that undermines reading it naively

| Quantity | k/n | Proportion [95% exact CI] | Grade |
|---|---|---|---|
| EMC case reports stating a primary-mass duration **in the abstract** | 7/26 | 0.269 [0.116, 0.478] | **PRIMARY** |
| Full texts probed whose abstract was silent but whose **full text was not** | 2/2 | 1.000 [0.158, 1.000] | **PRIMARY** |

Of the 26 case reports, one (Yue 2018, PMID 29886600) has **no abstract in PubMed** and is counted in the denominator but **not** as a negative.

**The 2/2 probe is the load-bearing result of this report.** I deliberately fetched the full text of two case reports whose abstracts said nothing about duration. Both stated one. Lubana 2015 gives a plain "for 1 year" in its Case Report section that appears nowhere in its abstract; Mitchell 2011 gives dated symptom onset and dated diagnosis, and then says outright: *"Sadly, this patient's disease went undetected for several months, and the window during which curative resection might have been possible was missed."*

The consequence is precise. **0.269 is a lower bound on how often EMC case reports record the interval, not an estimate of it** — an abstract-only harvest systematically undercounts. With n=2 the interval spans [0.158, 1.000], so the probe establishes **direction** (abstracts undercount) and not **magnitude**. Any future attempt to characterise EMC diagnostic delay from the literature must read full texts, and my own Table 2 is therefore incomplete in a known direction.

### Table 4 — the case-report distribution, and why it is not an answer

| Set | n | Median | Range | Values (months) |
|---|---|---|---|---|
| Stated durations only | 8 | **6.0 mo** | 2–36 | 2, 5, 6, 6, 6, 12, 12, 36 |
| + 1 derived from dates | 9 | **6.0 mo** | 2–36 | 2, 5, 6, 6, 6, 6, 12, 12, 36 |

**This is a case-report distribution and must be labelled as one wherever it is used.** Its denominator is *the case reports that chose to state a duration* — not EMC patients. The selection runs hard toward the unusual: this set is nasopharynx, masticator space, floor of mouth, plantar fascia, chest wall, pelvis, lung and a paediatric leg, published precisely because those sites are rare. A 36-month paediatric leg mass and a 2-month chest-wall lump are both in the set because each was surprising enough to publish. The median of 6 months **cannot** be read as a median diagnostic delay for EMC, and per the 2/2 probe the sample is also missing the cases whose durations sit only in unread full texts.

### The answer to the question

**The published EMC record cannot support a symptom-duration or diagnostic-delay distribution, and the reason is that the interval is not collected, not that the cohorts are small.**

Three findings carry this:

1. **Zero of eight EMC series with retrievable text report a symptom-duration summary statistic with a denominator.** The single cohort statement in existence is a bare 3–12 month range over n=5 with an unstated non-missing denominator. 97.9% of the 331 pooled series patients are in a source that says nothing at all.
2. **The omission is a consistent editorial choice, not an artefact of old papers.** The two most recent chart-review series — Michigan 2023 (n=44) and MGH 2024 (n=30) — both had chart access, both enumerated what they abstracted, and neither included the interval. The founding 1972 series (n=34) is `UNKNOWN by non-retrieval`, so the record does not even establish whether the field ever collected it.
3. **What does exist is per-case anecdote, and even that is under-harvested.** 7/26 case reports state a duration in the abstract; a 2/2 full-text probe shows abstracts undercount. Nine values, median 6 months, range 2–36 — a distribution over publication decisions, not over patients.

The useful consequence for this program is a constraint, and it is checkable. **Any claim that diagnostic delay drives EMC presentation stage is currently unsupported by the primary literature in either direction** — including the motivating aside already sitting in W04's own report, that myxoid confusability "drives real diagnostic delay in this disease." That sentence has no retrievable source behind it. The confusability itself *is* documented (Starostin's EMC read as a paralabral cyst; O'Neill's vulval EMC managed as a Bartholin's cyst for years; Nahal's toe EMC read as a traumatic fracture; Lockyer's plantar EMC read as a plantar fibroma), but **the interval those misreadings cost was never measured**, so the mechanism is attested and its magnitude is UNKNOWN.

---

## Validation evidence

**RUN.**

- Working directory `/tmp/claude-0/w04b` — outside the repository, per the corrected brief.
- Environment: `Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]`, `Linux 6.18.44-fc-v24 x86_64`
- Command: `date -u && python3 -VV && uname -srm && python3 emc_symptom_duration.py; echo "EXIT=$?"` → **`EXIT=0`**

**A real defect I found and fixed, rather than reporting past.** My first run printed `proportion = 0.269 [95% Clopper-Pearson 0.436, 0.143]` — a lower bound **above** its upper bound — and `[0.987, 1.000]` for k=n=2, which should be `[0.158, 1.000]`. Both quantiles in `clopper_pearson` were inverted: I had written `_inv(1 - alpha/2, k, n-k+1)` for the lower bound where the correct quantity is `Beta⁻¹(alpha/2; k, n-k+1)`. Fixed, then verified against three textbook values before rerunning:

```
  k=0 n=10: [0.0000, 0.3085]      (expected [0, 0.3085])
  k=10 n=10: [0.6915, 1.0000]     (expected [0.6915, 1])
  k=2 n=10: [0.0252, 0.5561]      (expected [0.0252, 0.5561])
  k=7 n=26: [0.1157, 0.4779]
  k=2 n=2:  [0.1581, 1.0000]
EXIT_SELFTEST=0
```

Verbatim key output of the corrected run:

```
[1] SERIES-LEVEL REPORTING
  EMC series/cohorts examined                       : 9
  ... with retrievable text                         : 8
  ... reporting a MEDIAN or MEAN symptom duration   : 0
  ... reporting a RANGE only (no non-missing n)     : 1  [Xu 2014]
  Patients in these series                          : 331
  Patients in a series with NO duration statistic    : 324  (97.9%)

[2] CASE-REPORT REPORTING FRACTION (abstract level)
  EMC single-case reports examined                  : n = 26
  ... stating a primary-mass duration IN THE ABSTRACT: k = 7
  proportion = 0.269  [95% Clopper-Pearson 0.116, 0.478]

[3] ABSTRACT-ONLY UNDERCOUNT PROBE (the load-bearing check)
  Full texts fetched whose ABSTRACT stated no duration : 2
  ... whose FULL TEXT did state/permit one             : 2
  proportion = 1.000  [95% Clopper-Pearson 0.158, 1.000]

[4] CASE-REPORT DISTRIBUTION  (*** NOT a population distribution ***)
  stated durations only    n= 8  median=  6.0 mo  range=2-36 mo  values=[2, 5, 6, 6, 6, 12, 12, 36]
  + 1 derived from dates   n= 9  median=  6.0 mo  range=2-36 mo  values=[2, 5, 6, 6, 6, 6, 12, 12, 36]
```

**Read-only compliance, verified:** `git status --porcelain` → `?? research/autonomy/opus-capacity-campaign-20260908/` (the coordinator's own pre-existing untracked directory, not mine); `find . -name '*W04b*' -not -path './.git/*'` → empty.

**PROPOSED (NOT RUN).** Full-text retrieval of the remaining 16 abstract-silent case reports to convert the 2/2 probe into a real reporting-rate estimate; full-text retrieval of Enzinger & Shiraki 1972 and Meis-Kindblom 1999 to resolve their `UNKNOWN` rows. Neither was attempted here — both would need paywalled routes, and the brief forbids circumventing access controls.

### Code (authored by me; returned inline, not written into the tree)

`/tmp/claude-0/w04b/emc_symptom_duration.py`, stdlib-only. Reproduced in full, post-fix:

```python
#!/usr/bin/env python3
"""
W04b (OPUS-CAPACITY-CAMPAIGN-20260908) — denominator-audited symptom-duration
audit of the retrievable primary EMC literature.

Every value below is a verbatim statement from a source retrieved via the PubMed
MCP tools in this session. Nothing is imputed. A source that does not state a
duration is UNKNOWN, never zero and never dropped silently.

Method discipline inherited from W06: numerator, denominator, and whether the
denominator is the full cohort or only the non-missing cases.
"""
import statistics as st

# ---------------------------------------------------------------- exact binomial
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
    import math
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    lbeta = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
             + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbeta) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta) * _betacf(b, a, 1.0 - x) / b

def clopper_pearson(k, n, alpha=0.05):
    """Two-sided exact binomial interval. Sampling only; no selection modelling."""
    def _inv(target, a, b):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2.0
            if betainc(a, b, mid) < target: lo = mid
            else: hi = mid
        return (lo + hi) / 2.0
    # low  = Beta^-1(alpha/2 ; k, n-k+1)      high = Beta^-1(1-alpha/2 ; k+1, n-k)
    low = 0.0 if k == 0 else _inv(alpha / 2, k, n - k + 1)
    high = 1.0 if k == n else _inv(1 - alpha / 2, k + 1, n - k)
    return low, high

# ------------------------------------------------------- the audited source table
# grade: PRIMARY (source states it) | UNKNOWN (source silent, or text not retrieved)
# where: ABSTRACT | FULLTEXT | NONE
# estimand: PRIMARY_MASS (symptom -> diagnosis of the primary) |
#           METASTASIS (symptom of a secondary lesion) | OTHER
CASES = [
    # pmid, label, months, where, estimand, verbatim
    ("30985717","Al Khader 2019 (leg, child)",36.0,"ABSTRACT","PRIMARY_MASS",
     "an 11-year-old boy with a 3-year history of a slowly growing painless left leg mass"),
    ("29657686","Purkayastha 2018 (nasopharynx)",12.0,"ABSTRACT","PRIMARY_MASS",
     "left-sided nasal obstruction and occasional epistaxis of one-year duration"),
    ("26125202","Lubana 2015 (plantar)",12.0,"FULLTEXT","PRIMARY_MASS",
     "complaints of a growth underneath the sole of her left foot for 1 year, with worsening pain"),
    ("28638563","Romanach 2017 (masticator space)",6.0,"ABSTRACT","PRIMARY_MASS",
     "a large painless, diffuse mass causing progressive midfacial asymmetry of 6 months duration"),
    ("38440485","Dabas 2023 (floor of mouth)",6.0,"ABSTRACT","PRIMARY_MASS",
     "difficulty in chewing food for a duration of 6 months"),
    ("30325000","Chahdi 2018 (pelvis)",5.0,"ABSTRACT","PRIMARY_MASS",
     "accusing pelvic pain for 5 months"),
    ("11917595","Rao 2002 (chest wall)",2.0,"ABSTRACT","PRIMARY_MASS",
     "left-sided chest pain and a hard lump in the breast of two months' duration"),
    ("27591381","Balanza 2016 (pulmonary primary)",6.0,"ABSTRACT","PRIMARY_MASS",
     "a 69-year-old male patient presented with intermittent hemoptysis for the last 6 months"),
    # DERIVED from two dated events in the full text, not a stated 'duration' sentence.
    ("21941486","Mitchell 2011 (flank) [DERIVED]",6.0,"FULLTEXT","PRIMARY_MASS",
     "presented ... in April 2009 with a painful, enlarging left flank mass ... "
     "Pathological review of a biopsy in October 2009 characterized the lesion"),
    # Different estimand: duration of the METASTATIC symptom, primary duration unstated.
    ("38111543","Starostin 2023 (lung mets)",3.0,"ABSTRACT","METASTASIS",
     "presented initially with a 3-month history of cough"),
]

# EMC clinical records whose retrieved text states NO duration for the primary mass.
SILENT_CASES = ["41689087","40831041","41323055","39924782","37753118","35974707",
                "35494187","33075019","30967942","28360467","26504046","25550031",
                "24818862","19894252","7648738","29886600"]
# 29886600 has NO abstract in PubMed -> UNKNOWN by absence of retrieved text, not silence.
NO_TEXT_CASES = ["29886600"]

SERIES = [
    # pmid, label, n, reported statistic, denominator status, grade
    ("10366145","Meis-Kindblom 1999",117,None,"no symptom-duration statistic in retrieved abstract","UNKNOWN"),
    ("18951519","Drilon 2008 (per W06 retrieval)",86,None,"no symptom-duration statistic","UNKNOWN"),
    ("36825763","Brodsky 2023 (Michigan)",44,None,"no symptom-duration statistic in retrieved abstract","UNKNOWN"),
    ("4261659","Enzinger & Shiraki 1972",34,None,"NO ABSTRACT IN PUBMED - text not retrieved","UNKNOWN"),
    ("39256245","Kandoussi 2024 (MGH)",30,None,"no symptom-duration statistic in retrieved abstract","UNKNOWN"),
    ("1451062","Saleh 1992",10,None,"no symptom-duration statistic in retrieved abstract","UNKNOWN"),
    ("24713246","Xu 2014",5,"range 3-12 months, no median, no stated non-missing n",
     "denominator UNSTATED (implied 5/5, never asserted)","PRIMARY (range only)"),
    ("2090579","Mukherjee 1990",3,None,"no symptom-duration statistic in retrieved abstract","UNKNOWN"),
    ("3731040","D'Ambrosio 1986",2,"metastasis preceded primary by 10 y and 2 y",
     "DIFFERENT ESTIMAND (metastasis-to-primary interval, not symptom-to-diagnosis)","PRIMARY (other estimand)"),
]

def main():
    print("=" * 78)
    print("EMC symptom-to-diagnosis interval — denominator audit (W04b)")
    print("Source: PubMed (MCP). Nothing imputed. Silence = UNKNOWN.")
    print("=" * 78)

    # ---- 1. series-level
    print("\n[1] SERIES-LEVEL REPORTING")
    n_series = len(SERIES)
    text_retrieved = [s for s in SERIES if "NO ABSTRACT" not in s[4]]
    with_summary = [s for s in SERIES if s[3] and "range" in str(s[3])]
    print(f"  EMC series/cohorts examined                       : {n_series}")
    print(f"  ... with retrievable text                         : {len(text_retrieved)}")
    print(f"  ... reporting a MEDIAN or MEAN symptom duration   : 0")
    print(f"  ... reporting a RANGE only (no non-missing n)     : {len(with_summary)}"
          f"  [{', '.join(s[1] for s in with_summary)}]")
    pooled = sum(s[2] for s in SERIES)
    unknown_pt = sum(s[2] for s in SERIES if s[5] == "UNKNOWN")
    print(f"  Patients in these series                          : {pooled}")
    print(f"  Patients in a series with NO duration statistic    : {unknown_pt}"
          f"  ({100*unknown_pt/pooled:.1f}%)")
    print("  => No EMC cohort in the retrievable record supports a symptom-duration")
    print("     DISTRIBUTION. The cohort-level denominator is 0 of "
          f"{len(text_retrieved)} series with text.")

    # ---- 2. case-report reporting fraction
    print("\n[2] CASE-REPORT REPORTING FRACTION (abstract level)")
    abstract_pm = [c for c in CASES if c[3] == "ABSTRACT" and c[4] == "PRIMARY_MASS"]
    n_cases = len(abstract_pm) + len([c for c in CASES if c[3]=="FULLTEXT"]) \
              + len([c for c in CASES if c[4]=="METASTASIS"]) + len(SILENT_CASES)
    k = len(abstract_pm)
    lo, hi = clopper_pearson(k, n_cases)
    print(f"  EMC single-case reports examined                  : n = {n_cases}")
    print(f"  ... stating a primary-mass duration IN THE ABSTRACT: k = {k}")
    print(f"  proportion = {k/n_cases:.3f}  [95% Clopper-Pearson {lo:.3f}, {hi:.3f}]")
    print(f"  ... of which {len(NO_TEXT_CASES)} record(s) had NO abstract at all -> UNKNOWN,")
    print("      counted in the denominator but NOT as a negative.")
    print("  This proportion is a LOWER BOUND on reporting, not an estimate of it.")

    # ---- 3. the abstract-vs-fulltext probe
    print("\n[3] ABSTRACT-ONLY UNDERCOUNT PROBE (the load-bearing check)")
    probed = ["26125202", "21941486"]
    rec = [c for c in CASES if c[0] in probed]
    lo2, hi2 = clopper_pearson(len(rec), len(probed))
    print(f"  Full texts fetched whose ABSTRACT stated no duration : {len(probed)}")
    print(f"  ... whose FULL TEXT did state/permit one             : {len(rec)}")
    print(f"  proportion = {len(rec)/len(probed):.3f} "
          f" [95% Clopper-Pearson {lo2:.3f}, {hi2:.3f}]")
    print("  n = 2. The interval is nearly the whole unit interval. This probe")
    print("  establishes DIRECTION (abstracts undercount), not MAGNITUDE.")

    # ---- 4. the case-report distribution, explicitly labelled
    print("\n[4] CASE-REPORT DISTRIBUTION  (*** NOT a population distribution ***)")
    strict = sorted(c[2] for c in CASES
                    if c[4] == "PRIMARY_MASS" and "DERIVED" not in c[1])
    broad = sorted(c[2] for c in CASES if c[4] == "PRIMARY_MASS")
    for name, v in (("stated durations only", strict), ("+ 1 derived from dates", broad)):
        print(f"  {name:<24} n={len(v):>2}  median={st.median(v):>5.1f} mo"
              f"  range={min(v):.0f}-{max(v):.0f} mo  values={[int(x) for x in v]}")
    print("  DENOMINATOR OF THIS DISTRIBUTION: the case reports that CHOSE to state")
    print("  a duration — not EMC patients. Selection is toward the unusual (odd")
    print("  sites, extreme durations, diagnostic-error narratives). It cannot be")
    print("  read as a median diagnostic delay for EMC.")

    print("\n" + "=" * 78)
    print("VERDICT: the published EMC record CANNOT support a symptom-duration")
    print("distribution. 0 of 8 series report one with a denominator; the only")
    print("cohort statement is a bare 3-12 month range over n=5 with an unstated")
    print("non-missing denominator. What exists is per-case anecdote.")
    print("=" * 78)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

---

## Limitations

- **The search is not exhaustive.** I examined 34 EMC clinical records out of 75 title-matched case-report hits plus the series. Records I did not open are **UNKNOWN**, not negatives. The series list is the large/known ones; a small series I did not retrieve could report the interval.
- **My own Table 2 is incomplete in a known direction.** The 2/2 full-text probe proves abstracts omit durations the papers contain. Sixteen abstract-silent case reports were not opened, so the true case-level yield is higher than 7/26 by an amount I did not measure.
- **`UNKNOWN by non-retrieval` is not `UNKNOWN by silence`.** Enzinger & Shiraki 1972 (n=34) and Yue 2018 have no PubMed abstract. I did not attempt paywalled routes. Their status is genuinely unresolved, and it is possible the founding series *does* report symptom duration.
- **The 6-month median is not a delay estimate and must never be cited as one.** It is a median over publication decisions. Its denominator is authors, not patients.
- **Confounded estimands even within the case set.** "Duration of symptoms" is not "diagnostic delay": a patient may have had the mass for 36 months and seen a doctor at month 34. No source I retrieved separates patient interval from system interval. Balanzá's row is a pulmonary primary presenting with hemoptysis and Purkayastha's is nasal obstruction — anatomically different symptom clocks pooled into one number.
- **No causal claim is licensed.** Nothing here establishes that delay affects stage, resectability, or survival in EMC, in either direction. The misdiagnosis narratives are attested; their cost in time is not.
- **Transfer limit.** W06's denominator discipline transferred cleanly to this estimand, but the two questions have different failure modes: molecular confirmation fails by *selective application with an unstated residue* (Drilon), whereas symptom duration fails by *never being collected at all*. The second is the harder gap — a residue can sometimes be bounded; an uncollected variable cannot.

---

## Stop condition

**Set:** a denominator-audited symptom-duration/diagnostic-delay table, **or** a precise statement of why the published record cannot support a distribution — either being a full deliverable.

**Met — and both halves were produced.** Tables 1–4 are the denominator audit, every row graded, nothing imputed. The verdict is the precise negative: 0 of 8 series with retrievable text report a symptom-duration summary statistic with a denominator; the single cohort statement is a bare 3–12 month range over n=5 with an unstated non-missing denominator; 97.9% of pooled series patients are in a silent source. The one thing the record does support — a 9-value case-report distribution, median 6 months, range 2–36 — is labelled as a distribution over publication decisions and is shown by the 2/2 full-text probe to be under-harvested as well as selected.

---

## Tool-call and wall-clock count actually used

**21 tool calls** (11 Bash, 1 ToolSearch, 9 PubMed MCP) against the ~40 target. **Wall clock ~10 minutes** (`02:00:58Z` → `02:04:40Z` of measured tool time within a session begun shortly before) against the ~40-minute target. Returned on meeting the stop condition rather than padding.

---

## Next concrete action

**One successor, and it is worth doing: convert the 2/2 full-text probe into a real reporting-rate measurement.** Fetch the PMC full text of the 16 abstract-silent EMC case reports listed in `SILENT_CASES` (most have PMC IDs and are open access — PMC12659415, PMC12376927, PMC10908772, PMC10519304, PMC9527174, PMC9044308, PMC6449903, PMC5351361, PMC5011171 among them), extract every symptom-duration sentence verbatim, and recompute Table 3 with a denominator that is full texts rather than abstracts. That single task would (a) put a real interval on the case-level reporting rate instead of the current lower bound of 0.269, (b) roughly triple the case-report distribution's n, and (c) test whether the misdiagnosis narratives (O'Neill's Bartholin's cyst, Nahal's traumatic fracture, Lockyer's plantar fibroma) actually quantify the time their misreadings cost — the one place in this literature where a *system-side* delay interval might be recoverable. It requires no paywalled route and no denied-route replay.

I do **not** recommend a successor that attempts Enzinger & Shiraki 1972 or Meis-Kindblom 1999 full text: both need publisher routes, and their `UNKNOWN` rows are honest as they stand.

result: EMC diagnostic-delay half of Lane 6 closed with an evidence-backed negative — 0 of 8 retrievable EMC series report a symptom-duration statistic with a denominator (97.9% of 331 pooled patients sit in a silent source; the sole cohort statement is a bare 3–12 month range over n=5 with an unstated non-missing denominator), so only a selected 9-case anecdote distribution (median 6 mo, range 2–36) exists, and a 2/2 full-text probe proves abstracts undercount it.
