> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

# W05d — Is tier B's conjunctivity load-bearing? A measured answer

## Worker

- **Worker:** W05d, LANE 5 refill (cross-study patient independence). Task: adjudicate, by construction, the rubric defect W10c flagged and declined to act on.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`), Claude Code 2.1.42, remote cloud container. I cannot observe the served model; the coordinator must extract the runtime model from the transcript. **No environment variable names a model.** No finding below depends on which model produced it.
- **`date -u` start:** `Tue Sep  8 02:26:12 UTC 2026`. **`date -u` end:** `Tue Sep  8 02:30:16 UTC 2026`.
- **HEAD actually read — and it moved under me, reported not smoothed.** The brief freezes the read commit at `92abbcb905cacf07f14b238db50d1b98f6590374`. At my start `git rev-parse HEAD` returned **`b9a0257e6acff53ad22535cf2adf261313e0b250`** (the same later commit W10c reported), with `git status --porcelain` showing the campaign `reports/` files untracked. At my end it returned **`47aac85f874a57a6f981c3432abcf16980968aec`** with a clean tree. The coordinator committed during my run. **The freeze does not hold.** All repository files I read (`research/data/emc-clinical-registry.json`, `systems/POLICY-evidence.md`, `research/modalities/emc-ipd-survival.json`) are non-campaign files and were not touched by either commit, so no finding here is affected; but the coordinator should know that no worker in this wave read the frozen tree.
- **Write isolation honoured.** Nothing written under `/home/user/Rare-cancers`. All execution in `/tmp/claude-0/w05d/`. `git status --porcelain` empty at end. No git write operation of any kind. No network egress at all — I made no PubMed MCP call, no `curl`, no `WebFetch`.
- `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — verbatim, with five proxy-exclusion variables (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy`) filtered for length only; they match on the `anthropic` substring inside long host lists and carry no model identity. Output identical at start and end:

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

## Question

**W05's tier B is conjunctive — disjoint institution AND disjoint accrual window AND disjoint identifier space. Is that conjunctivity a defect, or is it load-bearing?**

Open because W10c hit a pair (Oshiro 2000 vs `masunaga2025`) that scores tier C and licenses nothing even though, on W10c's reasoning, disjoint accrual on a shared time axis would physically exclude patient sharing on its own. W10c flagged it and explicitly declined to act. I do not own the rubric and have applied no change; this is a measured case routed to W05's owner.

**Answer, up front: the conjunctivity is load-bearing, and the measurement is unusually clean. Relaxing tier B to "disjoint accrual on a shared time axis, alone, suffices" would change ZERO verdicts on record. Of 465 cohort pairs in the committed corpus, exactly ONE would move under the relaxation — and it is a pair the repository's own records already flag as a possible patient-overlap. The relaxation's entire measured effect on this corpus is to produce one answer that the corpus separately says is probably wrong. Leave the conjunctivity alone.**

## Prior-work check

Read in full before any analysis: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `reports/W05-patient-independence-audit.md`, `reports/W05b-independence-reconciliation.md` (via W05c's transferred summary and the reports index), `reports/W05c-identifier-namespace-matrix.md`, `reports/W10c-oshiro-overlap-admissibility.md`. W05's four tiers are applied **exactly as written and unrelaxed** throughout; I scored nothing under a modified rubric.

Commands run and what they showed:

1. `grep -rn -i -E "accrual|studyPeriod|collection date|accrued" --include=... research/ systems/` (41 KB of output, campaign dir excluded) → confirms **no prior artifact in the corpus enumerates accrual-window documentation across cohorts**. The nearest things are per-record `studyPeriod` values in the registry and W10c's Asian-subset observation. This question is not already answered.
2. `python3` probe of `research/data/emc-clinical-registry.json` for `periodBasis|timeAxis|accrualAxis|periodAxis|studyPeriodBasis` → **all absent** (assertion A0). The registry schema has no field for the time axis at all. This is itself a finding, not a search failure.
3. `grep -rn -i -E "(accrual|study period|collected between|between 19xx and 20xx|19xx–20xx)" research/modalities research/manuscripts research/literature systems | grep -iE "GSE4303|GSE28866|GSE24369|GSE140686|SRP445369|Lund|Stanford|Heidelberg"` → **no hits**. Independently confirms W05c's finding that of the six retained molecular cohorts only `PRJNA1357027` documents a window.
4. `grep -rn -i "NCT03277924\|IMMUNOSARC" research/ systems/` → located the pre-existing overlap flag in `research/modalities/emc-ipd-survival.json` (see R4).

**Closed items I confirm I am not replaying.** I made **no** network request of any kind (no PubMed MCP call, no `curl`, no `WebFetch`), so no denied route was replayed. I did not touch PUB-EMC-CLASSIFICATION, any Brenca route, Hofvander/EGA, the restricted NR4A Perspective, the paired Davis negative, promoter transfer, lane-11 source-index material, Sunitinib 2014, Wagner 2020, CTARC 2022, Trabectedin/RT 2018, pazopanib primary, or the anthracycline paper. I attempted no patient, case or specimen identity. I did not re-derive GSE4303/GSE28866. **I added no case to any denominator.**

## Method / inputs

- Corpus: `/home/user/Rare-cancers`, read at `b9a0257e…` → `47aac85f…` (see HEAD note).
- Primary input: `research/data/emc-clinical-registry.json` → `registry.citations` (25 records, one a narrative review) and `registry.cohorts`.
- Transferred, cited not re-derived: the six retained molecular cohorts and their window-documentation status from `reports/W05c-identifier-namespace-matrix.md`; the `PRJNA1357027` collection-date window from `research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md:140` (`| Collection date | 1997–2020 |`), corroborated in `research/modalities/emc-fourth-cohort-route-readout.json:40` and `emc-fourth-cohort-quant.json:279`; Oshiro 2000's undocumented window from `reports/W10c-oshiro-overlap-admissibility.md`.
- Policy read before any pooling statement: `systems/POLICY-evidence.md` §2.3 (lines 164–177) and §2.7(d) (lines 267–268).
- Tool: one script I wrote and ran, `/tmp/claude-0/w05d/accrual_axis_matrix.py`, Python 3 stdlib, offline, outside the repository. Returned inline in Validation evidence.
- **Unit of analysis:** a "cohort" is one citation record or one deposited series — 24 clinical records (excluding the one narrative review), 6 molecular cohorts, plus Oshiro 2000 = **31 units, 465 pairs.**

## Result

### R1 — Accrual-window documentation, measured corpus-wide (PRIMARY)

W10c observed "five of seven Asian series document none". Measured across the whole corpus rather than the Asian subset:

| population | units | window documented | window UNDOCUMENTED | evidence class |
|---|---|---|---|---|
| clinical citation records (excl. 1 narrative review) | 24 | 12 | 12 | PRIMARY |
| retained molecular cohorts | 6 | 1 (`PRJNA1357027`, 1997–2020) | 5 | PRIMARY |
| unretained source (Oshiro 2000) | 1 | 0 | 1 | PRIMARY (transferred from W10c) |
| **total** | **31** | **13 (41.9%)** | **18 (58.1%)** | PRIMARY |

**Pairs: 465 total; 78 (16.8%) have both accrual windows documented. 387 (83.2%) do not, and are UNKNOWN on the accrual leg no matter what the rubric says.** W10c's Asian-subset rate (5/7 undocumented) is not an artifact of that subset — it is slightly *worse* than the corpus rate but the same order.

The 13 units with documented windows: `masunaga2025` [2002,2022], `ussc2022` [2000,2016], `chiusole2020` [1980,2018], `seer270_2022` [2004,2015], `drilon2008` [1975,2008], `uMich2023` [1998,2021], `bishop2019` [1990,2016], `apatinib2020` [2009,2019], `immunosarc2emc2025` [2020,2024], `stacchiotti2019pazopanib` [2014,2017], `palmerini2022trobsultrarare` [2010,2015], `martinbroto2020immunosarc1` [2017,2019], `PRJNA1357027` [1997,2020].

### R2 — The time axis is documented for **zero** of the 13 (PRIMARY, and this is the structural finding)

W10c's proposed relaxation turns on whether two windows sit on the **same time axis**. I probed the registry schema for any field recording that. **There is none** — no `periodBasis`, `timeAxis`, `accrualAxis`, `periodAxis` or `studyPeriodBasis` anywhere in the file (assertion A0, PASS). Every axis label below is therefore **INFERRED by me from the retained `design` and `population` strings**, at abstract strength, and is marked as such:

| axis class (INFERRED) | units | axis documentation status |
|---|---|---|
| `INSTITUTIONAL_TREATMENT` | `ussc2022`, `chiusole2020`, `drilon2008`, `uMich2023`, `bishop2019`, `apatinib2020` | INFERRED from "treated at", "retrospective review", "database" wording. UNKNOWN whether the window is diagnosis, presentation, resection or treatment start. |
| `TRIAL_ENROLMENT` | `immunosarc2emc2025`, `stacchiotti2019pazopanib`, `martinbroto2020immunosarc1` | INFERRED from trial design + registration ID. |
| `OBSERVATIONAL_REGISTRATION` | `palmerini2022trobsultrarare` | INFERRED (TrObs non-interventional registration). |
| `DIAGNOSIS` | `seer270_2022` | INFERRED from SEER convention. ⚠ CTARC 2022's methods are recorded unrecovered in `CLOSED-WORK.md`; I did not attempt retrieval and make no SEER-derived parameter claim. |
| `REGISTRY_ENTRY_or_DIAGNOSIS` | `masunaga2025` | **AMBIGUOUS — W10c's open question, unresolved here.** "Pathologically diagnosed EMC, JNBSTR, 2002-2022" does not say whether 2002–2022 is diagnosis year or registration year. |
| `SPECIMEN_COLLECTION` | `PRJNA1357027` | The one genuinely **DOCUMENTED** axis: the SRA record's own `Collection date` field. |

Machine result over the 78 both-documented pairs: **18 same inferred axis, 60 different inferred axis.** But "same axis" here is my inference, not a corpus fact, for 17 of those 18 pairs (all except any pair involving `PRJNA1357027`, and `PRJNA1357027` shares its axis with nothing). **Under the rubric's own standard — tier B requires each condition to be *individually documented* — the same-axis precondition of W10c's relaxation is documented for exactly 0 of 78 pairs.**

That alone is close to dispositive. A relaxation whose precondition the corpus never records is not a relaxation; it is a licence to infer the precondition, which is precisely what tier B was written to stop.

### R3 — Would the relaxation change any verdict on record? **No. Zero.** (PRIMARY)

Verdicts on record, enumerated: W05c's 15 molecular-cohort pairs (which subsume W05's rows 1v2, 3, 5), W10c's 8 Oshiro pairs, and W05's Filion 2009 ↔ Subramanian/GSE4303 row = **24 adjudicated pairs**.

| adjudicated set | pairs | both windows documented | could reach the relaxed antecedent |
|---|---|---|---|
| W05/W05c molecular pairs | 15 | 0 (only `PRJNA1357027` documents a window; its 5 pairs each have an undocumented counterpart) | 0 |
| W10c Oshiro pairs | 8 | 0 (Oshiro's own window is undocumented — W10c said so and I did not attempt to recover it) | 0 |
| W05 Filion ↔ GSE4303 | 1 | 0 (both undocumented) | 0 |
| **total** | **24** | **0** | **0** |

**VERDICTS THAT WOULD CHANGE UNDER THE RELAXATION: 0.** Machine-checked, exit 0. The conjunctivity currently costs the repository nothing at all: not one recorded UNKNOWN is caused by tier B insisting on institution and identifier alongside accrual.

W10c's own case is the clearest instance. Oshiro vs `masunaga2025` fails the relaxed rule at its antecedent — Oshiro's window is undocumented, so there is no "disjoint accrual" to relax onto. W10c noted this itself; my measurement confirms it generalises to every pair anyone has adjudicated.

### R4 — The one pair the relaxation *would* move, and why it is an argument against the change (PRIMARY)

Of the 78 both-documented pairs, 17 have genuinely disjoint windows; 3 are disjoint **and** same-inferred-axis; of those 3, two already have disjoint institutions (so the relaxation adds nothing — they were never held back by the institution leg). **Exactly one pair is disjoint, same-axis, and institution-NON-disjoint — i.e. exactly the shape W10c described, where the relaxation would move a verdict:**

> `immunosarc2emc2025` [2020,2024] **vs** `martinbroto2020immunosarc1` [2017,2019] — same inferred axis (`TRIAL_ENROLMENT`), shared network `NCT03277924` and shared Spanish/Italian/UK sites.

⛔ **And the repository already records this pair as a possible patient overlap.** `research/modalities/emc-ipd-survival.json`, `candidate_sources[12]`, verbatim:

> `"overlap_risk": "⚠ conference abstract; may be an expansion of martinbroto2020immunosarc1"`

The registry's own `design` string for `martinbroto2020immunosarc1` says it is *"stage 1 of the same registration as the IMMUNOSARC II EMC cohort"*. So the single pair on which the relaxation has any effect whatsoever is a pair where two arms of **one trial registration** report windows that are disjoint only at **year granularity across a single year boundary (2019 | 2020)**, and where the corpus separately holds a documented suspicion that the later cohort is an *expansion of* — not a replacement for — the earlier one. Relaxed tier B would license "these are disjoint patients" from year arithmetic, against a recorded overlap flag. That is a false licence, and it is the only licence the relaxation buys.

**Why the physical argument fails here, stated generally.** "Disjoint accrual on a shared axis excludes patient sharing" is sound only if each stated window is the *complete* accrual span of the patients each paper reports. A staged or expansion cohort violates that: the later report's stated window can describe its new accrual while its population includes earlier-accrued patients. The rubric's institution leg is what catches this — a shared trial network is exactly the condition under which the same person is accrued once and reported twice. Remove the conjunction and the catch goes with it.

Two further reasons the conjunctivity earns its place, both measured rather than asserted:

- **Granularity.** Every window in the corpus is stored as `[startYear, endYear]`. Adjacent windows are "disjoint" by construction whenever they abut at a year boundary. 1 of the 3 disjoint same-axis pairs abuts (2019|2020). A rule that licenses patient-disjointness from year arithmetic inherits that artifact.
- **Axis ambiguity is the norm, not the exception (R2).** Under a relaxed rule, the pressure moves from "document three things" to "assert that two windows are on the same axis" — an inference the corpus has no field to record and, in the one case that matters most (`masunaga2025`), cannot currently resolve.

### R5 — §2.3 makes part of the question moot, and I am saying so as instructed (PRIMARY)

`systems/POLICY-evidence.md` §2.3, verbatim:

> *"Across studies: single-institution series are often subsets of national or SEER registries. Where populations may overlap, the **smaller/overlapping** cohort is marked `pool: false` with `contextReason: "population-overlap"`."*

**This makes the *pooling* half of the question moot, and it does so for the exact pair in R4.** Whatever tier `immunosarc2emc2025` vs `martinbroto2020immunosarc1` scores, §2.3 already places the smaller/overlapping member outside the pooled denominator by default, and §2.7(d) binds it there for IPD. The relaxation could therefore not have changed a single pooled figure even in its one effective case.

What §2.3 does **not** make moot is the *wording* half — whether the repository may write "independent cohorts", "N distinct patients", or "replication in a second series". That is what W05's rubric governs and what a relaxation would loosen, and it is where the damage would land. The distinction matters: §2.3 protects the arithmetic; tier B protects the sentences.

**No pooled figure in this repository changes because of this report. I added no case to any denominator. No `pool` flag was inspected for modification and none was modified.**

### R6 — Recommendation to W05's owner (this is a recommendation, not a change)

**Keep tier B conjunctive.** Measured basis: it changes 0 of 24 recorded verdicts, its one effective case is a recorded overlap risk, and its same-axis precondition is documented for 0 of 78 candidate pairs.

If W05's owner nevertheless wants to reduce the friction W10c felt, the smallest correct repair is **not** a relaxation but an **addition**: give the registry schema a `periodBasis` field (`diagnosis` | `registration` | `treatment` | `enrolment` | `collection` | `unknown`, defaulting to `unknown`) so that the axis becomes a recorded fact rather than a reader's inference. That is a prerequisite for *any* future accrual-based reasoning and it costs no verdict today. ⛔ **I did not add it.** The registry is the clinical registry and `systems/POLICY-evidence.md` governs it; I am read-only, and this is W05's and the registry owner's call, not mine.

## Validation evidence

**RUN.** All execution in `/tmp/claude-0/w05d/`, outside the repository. Linux 6.18.44-fc-v24, container `container_0166QEHnXrRA8nCR59c9UG4k`, bash, Python 3 stdlib, ripgrep/grep. No network.

| # | command | exit | key output |
|---|---|---|---|
| 1 | `git rev-parse HEAD` (start) | 0 | `b9a0257e6acff53ad22535cf2adf261313e0b250` — **≠ frozen `92abbcb9…`** |
| 2 | `git rev-parse HEAD` (end) | 0 | `47aac85f874a57a6f981c3432abcf16980968aec` — **moved during my run** |
| 3 | `git status --porcelain` (end) | 0 | *(empty)* — nothing attributable to me |
| 4 | `date -u` | 0 | start `Tue Sep  8 02:26:12 UTC 2026`; end `Tue Sep  8 02:30:16 UTC 2026` |
| 5 | `sed -n '160,185p' systems/POLICY-evidence.md` | 0 | §2.3 quoted verbatim in R5 |
| 6 | python walk of `emc-clinical-registry.json` for `studyPeriod`/`studyPeriodUnknown` | 0 | 12 of 25 citation records carry a `studyPeriod`; `registry.cohorts` carries 11 more, all resolving to the same citations |
| 7 | `grep -rn -iE "(accrual\|study period\|collected between\|19xx–20xx)" research/modalities research/manuscripts research/literature systems \| grep -iE "GSE4303\|GSE28866\|GSE24369\|GSE140686\|SRP445369\|Lund\|Stanford"` | 0 | **no hits** — no molecular cohort but `PRJNA1357027` documents a window |
| 8 | `grep -rn -i "NCT03277924\|IMMUNOSARC" research/ systems/` | 0 | found `emc-ipd-survival.json:241` `"overlap_risk": "⚠ conference abstract; may be an expansion of martinbroto2020immunosarc1"` |
| 9 | **`python3 /tmp/claude-0/w05d/accrual_axis_matrix.py`** | **0** | full output below; **4 assertions passing, including one positive and two negative controls** |

Verbatim output of command 9 (`EXIT=0`):

```
A0 PASS: no time-axis field anywhere in the registry schema (probed periodBasis/timeAxis/accrualAxis/periodAxis/studyPeriodBasis)

cohort-bearing units in corpus: 31 (24 clinical citation records excl. 1 narrative review, 6 molecular cohorts, 1 unretained source)
units with a DOCUMENTED accrual window: 13
units with NO documented window:        18

all cohort pairs                       : 465
pairs with BOTH windows documented     : 78 (16.8% of all pairs)
A1 PASS: axis class coded for all 13 documented units
A2 PASS (negative control): undocumented units absent from the both-documented set

--- of the 78 both-documented pairs ---
same inferred time axis            : 18
different inferred time axis       : 60
windows actually disjoint          : 17
disjoint AND same inferred axis    : 3   <- antecedent of the proposed relaxation
  ... of those, institution SHARED : 1   <- pairs the relaxation would MOVE (C -> licensed)

pairs the relaxation would move (disjoint window, same axis, non-disjoint institution/network):
  immunosarc2emc2025 [2020, 2024]  vs  martinbroto2020immunosarc1 [2017, 2019]   axis=TRIAL_ENROLMENT  shared=['ES_IT_UK_SITES', 'NCT03277924_NETWORK']

pairs disjoint+same-axis with institutions ALSO disjoint (relaxation adds nothing - already tier-B eligible on that leg):
  apatinib2020 [2009, 2019]  vs  drilon2008 [1975, 2008]   axis=INSTITUTIONAL_TREATMENT
  immunosarc2emc2025 [2020, 2024]  vs  stacchiotti2019pazopanib [2014, 2017]   axis=TRIAL_ENROLMENT

--- verdicts on record ---
adjudicated pairs on record (W05/W05c 15 molecular + W10c 8 Oshiro + 1 Filion): 24
of those, pairs with BOTH windows documented (i.e. that could even reach the relaxed antecedent): 0
  -> NONE
VERDICTS THAT WOULD CHANGE UNDER THE RELAXATION: 0

A3 PASS (positive + negative control on the disjointness test): [2017,2019] vs [2020,2024] -> disjoint; [2002,2022] vs [2004,2015] -> not disjoint
```

The script `/tmp/claude-0/w05d/accrual_axis_matrix.py`, returned inline for the coordinator:

```python
#!/usr/bin/env python3
"""W05d - accrual-window documentation and time-axis matrix over the committed EMC corpus.

READ-ONLY. Reads research/data/emc-clinical-registry.json from the repository and a
hand-coded table of the six retained molecular cohorts + Oshiro 2000, whose provenance is
transferred from reports W05, W05c and W10c (cited, not re-derived).

Question: is W05 tier B's conjunctivity load-bearing? Answered by measuring how many cohort
pairs could even reach the antecedent of the proposed relaxation
("disjoint accrual on a shared time axis, alone, suffices").
"""
import json, sys, itertools

REPO = "/home/user/Rare-cancers"
REG = REPO + "/research/data/emc-clinical-registry.json"

# --- axis classes. AXIS IS INFERRED from the retained design/population string.
# The registry schema has NO field recording the time axis (asserted by A0 below).
AXIS = {
    "masunaga2025":            ("REGISTRY_ENTRY_or_DIAGNOSIS", "AMBIGUOUS"),
    "ussc2022":                ("INSTITUTIONAL_TREATMENT",     "INFERRED"),
    "chiusole2020":            ("INSTITUTIONAL_TREATMENT",     "INFERRED"),
    "seer270_2022":            ("DIAGNOSIS",                   "INFERRED"),
    "drilon2008":              ("INSTITUTIONAL_TREATMENT",     "INFERRED"),
    "uMich2023":               ("INSTITUTIONAL_TREATMENT",     "INFERRED"),
    "bishop2019":              ("INSTITUTIONAL_TREATMENT",     "INFERRED"),
    "apatinib2020":            ("INSTITUTIONAL_TREATMENT",     "INFERRED"),
    "immunosarc2emc2025":      ("TRIAL_ENROLMENT",             "INFERRED"),
    "martinbroto2020immunosarc1": ("TRIAL_ENROLMENT",          "INFERRED"),
    "stacchiotti2019pazopanib":("TRIAL_ENROLMENT",             "INFERRED"),
    "palmerini2022trobsultrarare": ("OBSERVATIONAL_REGISTRATION","INFERRED"),
    "PRJNA1357027":            ("SPECIMEN_COLLECTION",         "DOCUMENTED_ARCHIVE_FIELD"),
}

# institution / network identity, coded from the retained population string only.
INST = {
    "masunaga2025":            {"JP_NATIONAL_REGISTRY"},
    "ussc2022":                {"US_SARCOMA_COLLABORATIVE"},
    "chiusole2020":            {"IT_IOV", "FR_GUSTAVE_ROUSSY"},
    "seer270_2022":            {"US_SEER_POPULATION"},
    "drilon2008":              {"US_REFERRAL_A", "UK_REFERRAL_B"},
    "uMich2023":               {"US_UMICH"},
    "bishop2019":              {"US_SINGLE_INSTITUTION"},
    "apatinib2020":            {"CN_TWO_CENTRE"},
    "immunosarc2emc2025":      {"NCT03277924_NETWORK", "ES_IT_UK_SITES"},
    "martinbroto2020immunosarc1": {"NCT03277924_NETWORK", "ES_IT_UK_SITES"},
    "stacchiotti2019pazopanib":{"NCT02066285_NETWORK", "ES_IT_FR_SITES"},
    "palmerini2022trobsultrarare": {"NCT02793050_TROBS", "IT_SITES"},
    "PRJNA1357027":            {"TH_SIRIRAJ"},
}

# molecular cohorts retained (W05c). window documented? -> only PRJNA1357027.
MOLECULAR = {
    "GSE4303":      None, "GSE28866": None, "GSE24369": None,
    "GSE140686":    None, "SRP445369": None,
    "PRJNA1357027": [1997, 2020],   # SRA "Collection date" field, emc-fourth-cohort-sra-2026-08-08.md:140
}
EXTRA = {"oshiro2000": None}        # W10c's fifteenth source; window undocumented

def main():
    reg = json.load(open(REG))
    cites = reg["registry"]["citations"]

    # A0: the registry schema records no time axis anywhere.
    blob = json.dumps(reg)
    for probe in ("periodBasis", "timeAxis", "accrualAxis", "periodAxis", "studyPeriodBasis"):
        assert probe not in blob, "A0 FAILED: schema does name an axis field: " + probe
    print("A0 PASS: no time-axis field anywhere in the registry schema "
          "(probed periodBasis/timeAxis/accrualAxis/periodAxis/studyPeriodBasis)")

    units = {}
    for k, v in cites.items():
        if v.get("design") == "narrative review":
            continue
        units[k] = v.get("studyPeriod")
    n_clin = len(units)
    units.update(MOLECULAR); units.update(EXTRA)

    documented = {k: w for k, w in units.items() if w}
    print(f"\ncohort-bearing units in corpus: {len(units)} "
          f"({n_clin} clinical citation records excl. 1 narrative review, "
          f"{len(MOLECULAR)} molecular cohorts, {len(EXTRA)} unretained source)")
    print(f"units with a DOCUMENTED accrual window: {len(documented)}")
    print(f"units with NO documented window:        {len(units)-len(documented)}")

    all_pairs = list(itertools.combinations(sorted(units), 2))
    both = list(itertools.combinations(sorted(documented), 2))
    print(f"\nall cohort pairs                       : {len(all_pairs)}")
    print(f"pairs with BOTH windows documented     : {len(both)} "
          f"({100.0*len(both)/len(all_pairs):.1f}% of all pairs)")

    # A1: every documented unit has an axis coded
    for k in documented:
        assert k in AXIS, "A1 FAILED: no axis coded for " + k
    print("A1 PASS: axis class coded for all %d documented units" % len(documented))

    # A2: negative control - a unit with no window must never enter `both`
    flat = set(x for p in both for x in p)
    assert "GSE4303" not in flat and "oshiro2000" not in flat, "A2 FAILED"
    print("A2 PASS (negative control): undocumented units absent from the both-documented set")

    def disjoint(a, b):
        return a[1] < b[0] or b[1] < a[0]

    rows = []
    for x, y in both:
        wx, wy = documented[x], documented[y]
        ax, ay = AXIS[x][0], AXIS[y][0]
        same_axis = (ax == ay)
        inst_disj = len(INST[x] & INST[y]) == 0
        rows.append(dict(x=x, y=y, wx=wx, wy=wy, disj=disjoint(wx, wy),
                         ax=ax, ay=ay, same=same_axis, inst_disj=inst_disj))

    n_same = sum(r["same"] for r in rows)
    n_disj = sum(r["disj"] for r in rows)
    cand = [r for r in rows if r["disj"] and r["same"]]
    cand_shared_inst = [r for r in cand if not r["inst_disj"]]

    print(f"\n--- of the {len(both)} both-documented pairs ---")
    print(f"same inferred time axis            : {n_same}")
    print(f"different inferred time axis       : {len(both)-n_same}")
    print(f"windows actually disjoint          : {n_disj}")
    print(f"disjoint AND same inferred axis    : {len(cand)}   <- antecedent of the proposed relaxation")
    print(f"  ... of those, institution SHARED : {len(cand_shared_inst)}   <- pairs the relaxation would MOVE (C -> licensed)")

    print("\npairs the relaxation would move (disjoint window, same axis, non-disjoint institution/network):")
    if not cand_shared_inst:
        print("  (none)")
    for r in cand_shared_inst:
        print(f"  {r['x']} {r['wx']}  vs  {r['y']} {r['wy']}   axis={r['ax']}  shared={sorted(INST[r['x']]&INST[r['y']])}")

    print("\npairs disjoint+same-axis with institutions ALSO disjoint (relaxation adds nothing - already tier-B eligible on that leg):")
    for r in cand:
        if r["inst_disj"]:
            print(f"  {r['x']} {r['wx']}  vs  {r['y']} {r['wy']}   axis={r['ax']}")

    # --- verdicts on record ---
    W05C_MOL = list(itertools.combinations(sorted(MOLECULAR), 2))          # 15
    W10C = [("oshiro2000", k) for k in
            ["masunaga2025", "japan2003", "morioka2016trabectedin",
             "china2016", "huang2023", "apatinib2020", "jiang2026", "wang2026"]]
    FILION = [("filion2009", "GSE4303")]
    on_record = [tuple(sorted(p)) for p in W05C_MOL + W10C + FILION]
    print(f"\n--- verdicts on record ---")
    print(f"adjudicated pairs on record (W05/W05c 15 molecular + W10c {len(W10C)} Oshiro + 1 Filion): {len(on_record)}")
    win = dict(units); win["filion2009"] = None; win["japan2003"] = None
    movable = []
    for a, b in on_record:
        if win.get(a) and win.get(b):
            movable.append((a, b))
    print(f"of those, pairs with BOTH windows documented (i.e. that could even reach the relaxed antecedent): {len(movable)}")
    print(f"  -> {movable if movable else 'NONE'}")
    print(f"VERDICTS THAT WOULD CHANGE UNDER THE RELAXATION: {len(movable)}")

    # A3: positive control - the relaxation antecedent machinery does fire on a constructed case
    assert disjoint([2017, 2019], [2020, 2024]) is True, "A3 FAILED"
    assert disjoint([2002, 2022], [2004, 2015]) is False, "A3 FAILED"
    print("\nA3 PASS (positive + negative control on the disjointness test): "
          "[2017,2019] vs [2020,2024] -> disjoint; [2002,2022] vs [2004,2015] -> not disjoint")
    return 0

sys.exit(main())
```

**PROPOSED (NOT RUN):** adding a `periodBasis` enum to the registry schema and back-filling it for the 13 windowed units from each paper's Methods. Not run — I am read-only, the clinical registry is governed by `systems/POLICY-evidence.md`, and back-filling would require full texts that are recorded unrecovered.

**No test suite was run** — this changes no code and no shared state; per the brief I did not run `scripts/preflight.sh`. Nothing here is a skipped check reported as a pass. **No content-policy refusal was encountered.**

## Limitations

- **The axis classification in R2 is my inference for 12 of 13 units, and I do not upgrade it.** The corpus records no time axis. If W05's owner treats those inferences as data, the R4 count of movable pairs could differ; treated as the rubric requires (documented or not documented), the same-axis precondition is satisfied 0 times and the relaxation is inert by construction. Both readings support the same conclusion, which is why I report both.
- **UNKNOWN is not a soft yes.** 387 of 465 pairs cannot be evaluated on the accrual leg at all and stay UNKNOWN. I resolved none of them and claim no independence for any pair.
- **Institution-disjointness in R4 is coded from retained abstract-level population strings only.** For US pairs (`ussc2022`, `seer270_2022`, `uMich2023`, `bishop2019`) I coded distinct institution tokens because the corpus names distinct institutions — but whether a single-institution US series feeds a SEER registry, or belongs to the US Sarcoma Collaborative, is **UNKNOWN**, and §2.3 names exactly that hazard. Those pairs are therefore conservatively counted as institution-disjoint, which if anything *understates* the number of pairs the relaxation would wrongly move. The measured "1" is a floor, not a ceiling.
- **Windows are year-granular throughout.** No pair's disjointness is established below year resolution, and one of three disjoint same-axis pairs abuts at a year boundary.
- **I have no authority to relax the rubric and applied no change.** Every verdict cited is W05's, W05b's, W05c's or W10c's as written. I re-scored nothing.
- **No case entered any denominator, and no pooled figure changes.** §2.3 and §2.7(d) were read before any pooling statement and are quoted, not paraphrased.
- **No clinical claim.** Nothing here bears on prognosis, treatment, efficacy, safety, selectivity or clinical readiness. This is bookkeeping about patient-identity claims.
- **Transfer limit:** the molecular-cohort window status and Oshiro's undocumented window are transferred from W05c and W10c and re-checked by targeted grep (command 7), not re-derived from primary sources.

## Stop condition

**Set:** a measured count of pairs with both accrual windows documented, a same-axis/different-axis classification for each, and an explicit determination of whether relaxing conjunctivity would change any verdict on record.

**MET, all three.** (1) **78 of 465 pairs** have both windows documented, from 13 of 31 units — R1, machine-counted, exit 0. (2) Same/different axis classified for all 78 (18 same, 60 different, all inferred; axis documented for 0 of 78 as the rubric would require) — R2. (3) **Zero verdicts on record would change**; exactly one pair in the whole corpus would move, and it is a recorded overlap risk — R3, R4. The answer is the one the dispatch said was fully acceptable: **it would change none, so leave it** — with the added measurement that the one thing it *would* do is wrong.

## Tool-call and wall-clock count actually used

**27 tool calls** (all Bash; no MCP, no network, no ToolSearch) against a ~40 target. **Wall clock 4 minutes 4 seconds** (`date -u` 02:26:12 → 02:30:16 UTC) against a ~40-minute target. No padding, no sleeping.

## Next concrete action

**One task, for W05's owner and decisive rather than exploratory: adjudicate `immunosarc2emc2025` vs `martinbroto2020immunosarc1` explicitly under the rubric as written, and record the verdict.** It is the corpus's only both-documented, same-axis, disjoint-window, shared-institution pair; it carries an existing `overlap_risk` flag in `emc-ipd-survival.json` that no rubric verdict has ever been attached to; and both papers are open access (`PMC7674086` for stage 1; the IMMUNOSARC II abstract is retrievable from Crossref/Semantic Scholar per its own `retrievalNote`, with no denied route involved). Reading whether the 24 EMC patients in the stage-2 cohort include any stage-1 enrollee is a bounded yes/no read that either produces a tier-A non-overlap statement or converts the flag into an established `OVERLAPPING`. It is also the only case in the corpus where the conjunctivity question has any live consequence, so settling it retires the question rather than parking it.

⛔ Two things this successor is **not**: it is not authority to change the rubric — that stays with W05's owner, and my recommendation (R6: keep the conjunction; add a `periodBasis` field instead) is a recommendation only — and it is not a route to pooling either cohort, since §2.3 places the smaller/overlapping member at `pool: false` regardless of how the pair adjudicates.

---

result: Tier B's conjunctivity is load-bearing and should stay — measured, not argued. Of 31 cohort units in the committed corpus (24 clinical citation records, 6 molecular cohorts, Oshiro 2000), only 13 document an accrual window at all, so just 78 of 465 pairs (16.8%) have both windows documented; W10c's Asian-subset observation (5 of 7 undocumented) generalises to 18 of 31 units (58%) corpus-wide. The registry schema contains no field recording the time axis anywhere (probed periodBasis/timeAxis/accrualAxis/periodAxis/studyPeriodBasis, all absent), so axis is my inference for 12 of 13 units and documented for exactly one (PRJNA1357027's SRA Collection date) — meaning the same-axis precondition of the proposed relaxation is documented for 0 of 78 pairs. Relaxing tier B to "disjoint accrual on a shared time axis alone suffices" would change ZERO of the 24 verdicts on record (all 15 W05c molecular pairs, all 8 W10c Oshiro pairs and the Filion row fail the antecedent because one side's window is undocumented — including W10c's own motivating case). Exactly one pair in the entire corpus would move: immunosarc2emc2025 [2020,2024] vs martinbroto2020immunosarc1 [2017,2019] — same trial registration NCT03277924, shared Spanish/Italian/UK sites, windows disjoint only across a single year boundary — and research/modalities/emc-ipd-survival.json already records for it "⚠ conference abstract; may be an expansion of martinbroto2020immunosarc1", so the relaxation's sole measured effect is to license patient-disjointness against a documented overlap flag. POLICY-evidence §2.3 additionally moots the pooling half (the smaller/overlapping member is pool:false by default), leaving only the wording half at stake, which is exactly what tier B protects. Recommendation routed to W05's owner, not applied: keep the conjunction; if friction is the concern, add a periodBasis field to the registry rather than relax a tier. Script exit 0 with 4 assertions passing including one positive and two negative controls; no repository file written or edited; no network request of any kind; no case added to any denominator; HEAD moved b9a0257→47aac85 during the run, so the campaign freeze no longer holds.
