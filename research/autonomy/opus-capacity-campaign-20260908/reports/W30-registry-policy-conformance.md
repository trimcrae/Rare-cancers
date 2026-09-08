<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:23:46Z UTC
     agent id a31039470e5eeb98e ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a31039470e5eeb98e.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Audit complete; stop condition met. Report follows.

---

## Worker

**W30**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: evidence-contract conformance of the EMC clinical registry.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in my environment corroborates this; the coordinator must extract the served model from the transcript. No environment variable names a model.

**Start** — `date -u` → `Tue Sep  8 03:14:21 UTC 2026`; `git rev-parse HEAD` → `98a0833f1ede2cf9cef13790388260567a32e868`; `git status --porcelain` → 8 untracked campaign reports (W01g, W02f, W04e, W06f, W07f, W09f, W12e, W20g), no modifications.

**End** — `date -u` → `Tue Sep  8 03:18:31 UTC 2026`; `git rev-parse HEAD` → `5001d52a7dc8e4f37e7e050a677c48e823bc6c35` (**HEAD advanced under me** — the coordinator committed 20+ workers' reports); `git status --porcelain` → **empty**. Neither commit equals COMMON-BRIEF's frozen `92abbcb9…`; I read the checkout as it stands and say so.

**I verified the HEAD move did not affect anything I read:** `git diff --stat 98a0833f 5001d52a -- research/data/emc-clinical-registry.json systems/POLICY-evidence.md scripts/validate-registry.mjs research/meta/meta-analysis.mjs scripts/preflight.sh` returned **empty output, exit 0** — all five inputs byte-identical across the move. What moved was other workers' reports. One consequence matters below: `W07f-emc-only-cohort-full-texts.md` was **untracked at my start HEAD and committed at my end HEAD**, so its status as "committed evidence" changed mid-run; I state which HEAD each claim is anchored to.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (identical at start and end; the four long `*no_proxy*`/`JAVA_TOOL_OPTIONS` lines are elided here as pure proxy noise and were shown in full in the start capture):

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

**Write isolation honoured: zero repository writes, zero git write operations.** All execution under `/tmp/claude-0/w30/` (one file, `audit.py`). `git status --porcelain` was empty at end.

## Question

**Does `research/data/emc-clinical-registry.json` conform to `systems/POLICY-evidence.md`, requirement by requirement and row by row — and does `scripts/validate-registry.mjs` actually enforce that policy, or only a subset?**

Open because the policy is a prose contract of ~24 distinct requirements while the validator is 170 lines, and because the validator's own header asserts it enforces "the evidence contract" without ever enumerating what it leaves unenforced. A gate that passes tells you nothing about the requirements it never looks at.

## Prior-work check

Commands run (read-only):

```
$ git log --oneline -S'morioka2016trabectedin' -- research/data/emc-clinical-registry.json
14a3f172 -s ours x15: every stranded branch read by identity, and none of them holds anything
$ git log --oneline -- research/data/emc-clinical-registry.json | wc -l
1
$ grep -rn "masunaga" --include=*.md --include=*.json --include=*.mjs --include=*.py -il   (40 files)
$ grep -rn -E "\b(134|128|171|163)\b" research/manuscripts/*.md research/meta/*.mjs | grep -iE "masunaga|registry|localis|localiz|cohort|n="
```

The registry's Git history is **squashed to a single commit** (`14a3f172`, 2026-09-04), so `git log -S` and `git blame` cannot date any individual field. Every contradiction below is therefore reported as a **state** of the committed file, never as a drift with a direction — I cannot tell which of two contradicting fields was written first.

Read in full: `systems/POLICY-evidence.md`, `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, and reports W06e, W06f, W07e, W07f, W08h (the last three by targeted grep of their finding sections plus full read of W07f §5.2–5.5).

**Confirmed not replayed:** the user-rejected registry ICD-O classification paper (I ran no classification analysis and propose no row); every unrecovered source in CLOSED-WORK (Pazopanib full paper, Sunitinib 2014, Trabectedin/RT 2018, Wagner 2020, CTARC 2022, anthracycline) — **I retrieved no article content at all**, only identifier conversions; GSE4303/GSE28866; lane 11's source index; the blocked NR4A Perspective. **No denied route replayed.** W06e's registry read (that the registry states no confidence interval on any survival percentage) is reused as a stated input, not re-derived.

**Overlap declared:** W07f already established Morioka's arm structure from full text and its Next-action names the correction. My finding F1 below is **not** that discovery; it is the distinct observation that the contradiction also exists **inside the committed registry**, between two of its own fields, and is therefore repairable without any retrieval.

## Method and inputs

**Files read** (all at `98a0833f`, all verified byte-identical at `5001d52a`):

- `/home/user/Rare-cancers/systems/POLICY-evidence.md` (387 lines) — the requirement source
- `/home/user/Rare-cancers/research/data/emc-clinical-registry.json` (103,203 bytes) — the object audited
- `/home/user/Rare-cancers/scripts/validate-registry.mjs` (170 lines) — read in full, both halves
- `/home/user/Rare-cancers/scripts/preflight.sh` — gate-order enumeration only
- `/home/user/Rare-cancers/research/meta/meta-analysis.mjs` — grep for what it consumes
- `/home/user/Rare-cancers/research/manuscripts/emc-mortality-mechanisms.md`, `…-paper.md` — cross-artifact count check

**Tool:** `python3` (system), one scratch script `/tmp/claude-0/w30/audit.py`, executed outside the repository. `node scripts/validate-registry.mjs`, which reads one file and writes to stdout only — **it performs no filesystem write**, and `git status --porcelain` was empty after it ran.

**Retrieval:** two `mcp__PubMed__convert_article_ids` calls, identifier-guard only. **No content retrieval of any kind**, so no full-text, abstract or metadata fact is asserted from PubMed in this report — the guard is used solely to test the registry's own §1.2 resolvability claim.

**Denominators used throughout** (counted from the file, not remembered): **25** citations, **14** cohorts (**5** pooled / **9** context), **4** patient rows, **2** `evidenceQuestions` carrying **9** positions, **10** `treatments.systemicEvidence` rows, **6** `emergingTreatments.items`, **11** `studies.items`. Total citation-bearing rows: **37**.

## Result

### 5.1 Headline

**On every requirement of `POLICY-evidence.md` that can be decided from committed data, the registry conforms: 0 violations across all machine-checkable requirements, on the denominators tabulated below.** The validator agrees — `node scripts/validate-registry.mjs` exits **0** with **0 errors and 0 warnings**. That is a clean audit of a clinical registry and it is worth stating plainly.

Three things sit alongside that clean result and none of them is a policy violation as the policy is written:

- **F1** — one **internal contradiction between two committed fields of the registry itself** about the composition of the Morioka trabectedin arm (§5.3). This is the item the dispatch asked me to look for, and it exists.
- **F2** — **4 of 8 `provenance:"secondary"` rows** name a primary that is *already present in the same file* as a verified citation entry, so §1.3's "then add a real citation entry and **repoint** `sourceId`" is half-done for them (§5.4).
- **F3** — the validator's own header comment misstates its position in `preflight.sh` (§5.6), confirming in a fourth location the ordinal drift `POLICY-evidence.md` already flags.

### 5.2 Requirement-by-requirement conformance table

Every row is `PRIMARY` as a statement about repository state (I read the bytes). "UNEVAL" = cannot be decided from committed data without retrieving the source; it is **UNKNOWN, not a pass and not a fail**.

| # | Policy requirement (§) | Satisfy | Violate | Uneval | Denominator |
|---|---|---|---|---|---|
| R1a | Citation has `title` (§1.2) | 25 | **0** | 0 | 25 citations |
| R1b | Citation has `year` (§1.2) | 25 | **0** | 0 | 25 |
| R1c | Citation has `url` (§1.2) | 25 | **0** | 0 | 25 |
| R1d | ≥1 resolvable id `pmid\|pmcid\|doi` (§1.2) | 25 | **0** | 0 | 25 |
| R1e | `license` recorded (§1.2) | 25 | **0** | 0 | 25 |
| R1f | Recorded ids mutually consistent at NCBI (§1.2, my added test) | 14 | **0** | 11 | 25 |
| R2a | Patient row cites by `sourceId`, resolves (§1.1) | 4 | **0** | 0 | 4 patients |
| R2b | Cohort cites by `sourceId`, resolves (§1.1) | 14 | **0** | 0 | 14 cohorts |
| R2c | `systemicEvidence` row `sourceId` resolves (§1.1) | 10 | **0** | 0 | 10 |
| R2d | `evidenceQuestions` position `sourceId` resolves (§3) | 9 | **0** | 0 | 9 positions |
| R3a | `provenance:"secondary"` ⇒ `primaryRef` (§1.3) | 8 | **0** | 0 | 8 secondary rows |
| R3b | `sourceId` is the document actually read (§1.3) | — | — | **37** | 37 rows — **not decidable from committed data** |
| R3c | No invented identifier for an unfetched primary (§1.3) | 8 | **0** | 0 | 8 — all `primaryRef` values are plain text, zero carry a PMID/DOI |
| R3d | Primary pulled ⇒ citation added **and** `sourceId` repointed (§1.3) | 4 | see **F2** | 0 | 8 — 4 rows name a primary already present as a verified citation |
| R4a | Pooled cohort has explicit integer `{events,denom}`, `events≤denom` (§2.1.2) | 5 | **0** | 0 | 5 pooled |
| R4b | No pooled cohort carries a percentage-only field (§2.1.2) | 5 | **0** | 0 | 5 — zero `*Pct`/`*Text` on any pooled row |
| R4c | Context row states `contextReason` (§2.1) | 9 | **0** | 0 | 9 context |
| R5a | Confirmed EMC, molecular/histological (§2.1.1) | 5 | **0** | 0 | 5 — all 5 sources are EMC-titled series; **histology not re-verified by me** |
| R5b | Outcome ≠ inclusion criterion (§2.1.3) | 5 | **0** | 0 | 5 — the metastatic-at-diagnosis stratum reports **no** metastasis metric, exactly as §2.1.3 requires |
| R6a | Within-study pooled strata disjoint on `populationKey`+`stratum` (§2.3) | 5 | **0** | 0 | 5 pooled, 5 distinct keys, 0 collisions |
| R6b | Across-study population overlap resolved (§2.3) | 3 | **0** | **2** | 5 pooled — see §5.5 |
| R7a | Cohort `studyPeriod` valid shape, or `studyPeriodUnknown` (§4.1) | 12 | **0** | **2** | 14 — cohorts[7], cohorts[8] carry neither |
| R7b | `studyPeriod` recorded only from what the source states (§4.1) | — | — | **14** | 14 — **not decidable without the sources** |
| R7c | Citation-level `studyPeriod` | 12 | **0** | 13 | 25 — absence is permitted by §4.1 |
| R8a | Time-anchored survival never merged (§2.4) | — | **0** | 0 | 5-yr/10-yr figures appear **per row only**; `meta-analysis.mjs` consumes only `{events,denom}` |
| R9a | `contested` ⇒ ≥2 opposing stances (§3) | 1 | **0** | 0 | 1 contested question (stances: supports, supports, against, against, against) |
| R9b | Every position names the mechanism of conflict (§3) | 9 | **0** | 0 | 9 — all carry `caveat`/`design` |
| R9c | `bottomLine` present (§3) | 2 | **0** | 0 | 2 questions |
| R10 | Disease-death + other-cause-death partition ≤ n (validator invariant) | 2 | **0** | 0 | 2 cohorts carrying both |
| R11 | `verified` flag present on citation (§1.3) | 25 | **0** | 0 | 25 — **all 25 are `true`; zero are `false`.** See Limitation 2 |

**§2.6 (study-level descriptive series, requirements a–h) and §2.7 (reconstructed patient-level survival, a–f) are not exercised by this file at all** — the registry contains no descriptive series and no reconstructed IPD. Denominator **0** for both sections. That is not conformance and not violation; those classes live in other artifacts and are out of my scope.

### 5.3 F1 — the one cross-artifact contradiction: the Morioka trabectedin arm

The dispatch asked specifically whether any row's recorded cohort composition, patient count or arm structure is contradicted by another committed artifact. **One is.** Both fields are in the same file, in the same single commit, so neither can be called the later drift.

**Field A — `registry.citations.morioka2016trabectedin`** (`"n": 5`, `"verified": true`):

> `"population": "subjects with EMCS OR mesenchymal chondrosarcoma allocated to trabectedin; the EMC share of the 5 is not stated"`

**Field B — `treatments.systemicEvidence[6]`, agent "Trabectedin"** (`"n": 2`, `sourceId: morioka2016trabectedin`, `provenance: "primary"`):

> `"nBasis": "the EMC subjects of a 5-subject trabectedin arm that also contained 3 mesenchymal chondrosarcoma patients"`
> `"result": "… The full text's Methods state the split - two EMC subjects and three mesenchymal chondrosarcoma subjects - and Table 2 gives each individually. Both EMC subjects had stable disease, with PFS of 13.0 and 7.4 months …"`

These cannot both be true. Field A asserts the source **does not state** the EMC share of the 5; Field B asserts the source's **Methods state** it, and then reports per-patient outcomes for the two it names. The arm structure claimed by the citation entry (5 EMCS-or-MCS, split unknown) and by the evidence row (2 EMC + 3 MCS, split known) are different objects.

**Severity, stated honestly.** No pooled proportion or interval depends on this: the trabectedin row is `n=2` with `orrEvents: 0`, it is not a `registry.cohorts` entry, and `meta-analysis.mjs` consumes only `registry.cohorts` rows with `pool !== false` — I verified that at `research/meta/meta-analysis.mjs:32`. **Nothing pooled changes.** What is damaged is the provenance record: `verified: true` on this citation is, per §1.3, a claim that a human or agent opened the link and confirmed it supports *the exact claim* — and the file makes two mutually exclusive claims about that same source under that one flag. This is precisely the object-confusion the dispatch names: `verified: true` is a record of a past check, not a present verification, and here the past check cannot have confirmed both.

**Corroboration and its exact status.** `W07f-emc-only-cohort-full-texts.md` §5.2 reports reading `PMC4946242` at full text through PubMed MCP and quotes the Methods verbatim: *"The number of subjects with EMCS and MCS was 2 (2.7 %) and 6 (8.2 %), respectively. Five subjects with EMCS and MCS were allocated to the trabectedin group."* **That sentence states the whole-trial histology counts (2 EMCS, 6 MCS across both arms) and the trabectedin allocation (5) — it does not itself state the arm's split**, and W07f separately records that *"Subject No. 1's histology is UNKNOWN from this route."* So the source text W07f retrieved supports Field A's caution at least as well as Field B's confidence about the *Methods*; Field B's per-patient outcomes must come from Table 2, which W07f could read only in part. **I did not retrieve the article and I do not adjudicate which field is right.** I report only that the committed registry contradicts itself, and that the contradiction is resolvable from a source the campaign has already shown to be reachable at $0.

W07f was **untracked at my start HEAD `98a0833f` and committed at my end HEAD `5001d52a`** — so as of the end of my run there are two committed artifacts in tension with `citations.morioka2016trabectedin.population`, one of them the registry's own `systemicEvidence` row.

### 5.4 F2 — §1.3's repoint step is half-done for 4 of 8 secondary rows

§1.3: *"Do not invent an identifier for a primary you have not actually fetched and verified. Leave it as `primaryRef` text until you pull it; **then add a real citation entry and repoint `sourceId`**."*

Zero rows invent an identifier — R3c is clean, all 8 `primaryRef` values are plain author-year text. But for 4 of the 8, the primary **has** since been pulled and now sits in `registry.citations` as a `verified: true` entry, while the row still attributes its numbers to the review:

| Row | `sourceId` (what it cites) | `primaryRef` (what it read about) | Primary already in `registry.citations`? |
|---|---|---|---|
| `cohorts[8]` "Advanced disease on pazopanib", n=26 | `remiszewski2025` (review) | "Stacchiotti et al., Lancet Oncol 2019 phase 2 (n=26)" | **YES — `stacchiotti2019pazopanib`**, PMID 31331701, `verified: true` |
| `evidenceQuestions[0].positions[3]` | `remiszewski2025` | "Drilon et al." | **YES — `drilon2008`**, PMID 18951519, `verified: true` |
| `evidenceQuestions[1].positions[1]` | `remiszewski2025` | "Chiusole et al." | **YES — `chiusole2020`**, PMID 32612944, `verified: true` |
| `treatments.systemicEvidence[8]` "Immune checkpoint inhibitors" | `remiszewski2025` | "…and `galitskiy2025emcpembrolizumab` for the single-agent case" | **YES — names the citation key in prose** |
| `cohorts[6]`, `eq[0].positions[1]` | `remiszewski2025` | "Kemmerer et al. (SEER 2004-2012)" | no |
| `cohorts[7]` | `remiszewski2025` | "Giner et al. (n=31)" | no |
| `eq[1].positions[2]` | `remiszewski2025` | "Wagner et al. (SEER 1973-2016)" | no — and CLOSED-WORK records Wagner 2020 methods as unresolved |

The four "no" rows are **correct as they stand**: §1.3 explicitly says leave it as `primaryRef` text until you pull it, and those three primaries have not been pulled. The four "yes" rows are the ones where the contract's own next step was not taken. `cohorts[8]` is the one that carries numbers a reader might quote — n=26, ORR 18%, median PFS 19 months, 2-yr OS 90% — attributed to a narrative review while the phase-2 primary sits three keys away in the same file, verified.

**This is a conformance gap, not laundering.** Every one of these rows is honestly labelled `provenance: "secondary"` and names its primary in plain text, which is exactly what §1.3 demands of an *unpulled* primary. Nothing is disguised. The defect is an unfinished upgrade, and the validator cannot see it because it never compares `primaryRef` text against the citation map.

### 5.5 Cross-artifact count reconciliation — everything else checks out

I checked every count-bearing row against the other committed artifacts that carry the same numbers. **All consistent:**

- **Masunaga strata.** `cohorts[0]` n=134 + `cohorts[1]` n=29 = 163, against `citations.masunaga2025.n` = **171**. The gap is 8 and `cohorts[0].note` states it: *"8 non-surgically-treated localised cases excluded."* 134 + 8 + 29 = 171. **Reconciles.**
- **Masunaga mortality arithmetic**, entirely within the two `otherCauseDeathNote` fields: localised 88+28+8+4 = 128 non-chemo, +6 chemo = 134; disease deaths 8+1 = **9** ✓, other-cause 4+0 = **4** ✓. Metastatic 1+9+5+1 = 16 chemo, +13 non-chemo = 29; disease deaths 5+4 = **9** ✓, other-cause 1+0 = **1** ✓. **Every published sub-count sums to its stated denominator.**
- **Against the manuscripts.** `emc-mortality-mechanisms.md:72` and `…-paper.md:239` both carry `134 | 9 | 4`; `emc-mortality-mechanisms.md:116` carries `3.0 % (4/134)`. **Identical to the registry.**
- **Chiusole.** `cohorts[4]` n=49 vs `citations.chiusole2020.n` = 59; the note states *"49 curative-intent patients (of 59)."* **Reconciles.**
- **Against the meta-analysis.** `meta-analysis.mjs:99` hard-codes `prisma = { … pooled: 5, context: 9, cases: 4 … }`. My independent census of the file: **5 pooled, 9 context, 4 patient rows.** **Exact match on all three.**
- **The remaining 10 cohorts** match their citation `n` exactly (117, 60, 41, 270, 87, 44, 42, 40) or are secondary rows whose citation carries no `n`.
- **All 10 `systemicEvidence` rows** reconcile with their citation's `n` through an explicit `nBasis` string (24 accrued/23 evaluable; 26 started/23 mITT/22 evaluable; 11 enrolled/10 evaluable; 3 EMC of 33; 3 EMC of 36) — **except** the Morioka row, F1.

**Two overlap determinations I could not make (R6b, UNEVAL=2).** `cohorts[2]` (Meis-Kindblom, 117 AFIP consultation cases, `studyPeriodUnknown: true`) is pooled alongside `cohorts[3]` (US Sarcoma Collaborative 2000–2016) and `cohorts[4]` (Padova + Gustave Roussy 1980–2018). A worldwide consultation series can in principle contain cases that later entered an institutional database. The registry declares no overlap; nothing committed lets me confirm or refute that, because neither Meis-Kindblom's contributing institutions nor its diagnosis years are recorded anywhere in this tree. **UNKNOWN, not a violation.** The registry does handle every overlap it *can* see — Bishop, SEER-270 and U Michigan are all `pool: false` with `contextReason: "population-overlap"`.

### 5.6 Does the validator enforce the policy, or a subset? — A subset, and here is which

Read in full: `scripts/validate-registry.mjs`, 170 lines. Verdict: **it enforces the structural half of §1 and §3 and part of §2.1/§2.3/§4.1; it enforces nothing at all from §2.2, §2.4, §2.5, §2.6 or §2.7.** Of the 24 distinct requirements I could enumerate from the policy text, it checks **9 as hard errors**, **3 as warnings only**, and **12 not at all**.

**Checked as ERROR (exit 1):**

1. `registry.dataStatus` in the allowed enum, and `SAMPLE_SYNTHETIC` ⇒ `dataStatusBanner` — a validator invariant, not stated in the policy prose.
2. §1.2 citation `title`, `year`, `url`, and ≥1 of `pmid|pmcid|doi`.
3. §1.1 `sourceId` resolves — for `patients`, `cohorts`, `evidenceQuestions[].positions[]` and `treatments.systemicEvidence[]`.
4. §1.3 `provenance:"secondary"` ⇒ `primaryRef` present — for cohorts, positions and systemicEvidence.
5. §2.1.2 partial: where a metric key exists, `events` and `denom` are numbers and `events ≤ denom`.
6. The `diseaseDeath`/`otherCauseDeath` partition: same denominator, and sum ≤ n.
7. §4.1 partial: `studyPeriod` is `[int,int]` with `start ≤ end ≤ currentYear+1`.
8. §3: `consensus` in enum, ≥1 position, valid `stance`, `claim` present, and `contested` ⇒ both a `supports` and an `against` (or a `mixed`).
9. Presence checks on `studies.items[].url/.title`, `emergingTreatments.items[].name`, `systemicEvidence[].agent`, `cohorts[].label`, numeric `cohorts[].n`, and the five required patient fields.

**Checked as WARNING only (does not fail the gate):**

10. §1.2 `license` recorded — the policy says "Record the `license`"; the validator downgrades it to a warn.
11. §2.1 `pool:false` without `contextReason` — the policy's §5 checklist states this as a requirement.
12. **§2.3 within-study double-counting** — two pooled cohorts sharing `populationKey`+`stratum` produce a **warning, not an error**. The policy calls double-counting *"the cardinal sin of pooling"*; the gate would let it through. It also only fires when `populationKey` is *set*: a pooled cohort with no `populationKey` is silently exempt. (Both currently moot — all 5 pooled cohorts set a key and all 5 keys are distinct.)
13. §4.1 pooled cohort with neither `studyPeriod` nor `studyPeriodUnknown` — warn. Context rows are **not checked at all**, which is why `cohorts[7]` and `cohorts[8]` carrying neither field passes silently (my R7a UNEVAL=2).

**NOT checked at all — the twelve:**

14. §1.3 "`sourceId` is the document you actually read the number in" — unenforceable in principle, and not approximated.
15. §1.3 "**then add a real citation entry and repoint `sourceId`**" — no comparison of `primaryRef` text against the citation map. **This is why F2 is invisible to the gate.**
16. §1.3 `verified: true` only when the link was opened and supports the exact claim — **the validator never reads the `verified` field.** All 25 citations claim `true`; the gate would report OK if all 25 claimed `true` falsely. **This is why F1 is invisible to the gate.**
17. §2.1.1 confirmed EMC.
18. §2.1.2 "we never derive counts from a published percentage" — a pooled row carrying `recurrencePct` alongside `{events,denom}` would pass. (No row does.)
19. §2.1.3 outcome ≠ inclusion criterion — nothing compares `criteria.stage` against which metric keys are present. A `stage:"distant"` cohort reporting a `metastasis` metric would pass silently. (`cohorts[1]` correctly omits it — by authorship, not by enforcement.)
20. §2.1.4 / §2.3 **across-study** population overlap — no check whatsoever.
21. §2.2 the pooled proportion and the Wilson interval — the validator computes no statistic and never touches `meta-analysis.mjs`, so nothing links the two pooling methods §2 warns are non-interchangeable.
22. §2.4 time-anchored survival never merged — `fiveYearDSS` and `dssText` are never inspected.
23. §2.5 the stated limitations.
24. §2.6 (a)–(h) study-level descriptive series and §2.7 (a)–(f) reconstructed IPD — **zero coverage**, including §2.7(a)'s mandatory numbers-at-risk table and §2.7(b)'s reproduce-your-own-input requirement, which are refusal conditions the policy states in the strongest language it uses anywhere.

**Integer-type note.** §2.1.2 requires *"explicit integer counts"*. The validator tests `typeof m.events !== "number"`, which accepts `16.5`. Not exploited — I confirmed all 22 count values across the 5 pooled cohorts are Python `int` after `json.load`.

**F3 — the validator's header misstates its own gate position.** `validate-registry.mjs:15` asserts *"It is also gate 2 of `scripts/preflight.sh`."* `POLICY-evidence.md:31-33` asserts gate **10**, adding *"because this ordinal had four homes and three of them said 2."* I enumerated `preflight.sh`'s gate banners: `grep -n '^echo "== ' scripts/preflight.sh | cat -n` puts `== validate (EMC clinical registry evidence contract) ==` at **line 722, the 10th banner of 17**. **The policy is right; the validator's own comment is one of the three stale homes it warns about.** Cosmetic, but it is a comment that tells a future reader the wrong thing about the gate they are relying on.

## Validation evidence

### RUN

**V1 — start/end state.** `date -u`, `git rev-parse HEAD`, `git status --porcelain`, `env | grep …` — all quoted verbatim in §Worker. `git diff --stat 98a0833f… 5001d52a… -- <5 input files>` → **empty output, exit 0**.

**V2 — the conformance audit.** `python3 /tmp/claude-0/w30/audit.py` → **exit 0**. Key verbatim output:

```
R1.title  SAT=25 VIO=0 UNEVAL=0 DENOM=25
R1.resolvable-id  SAT=25 VIO=0 UNEVAL=0 DENOM=25
R1.license-recorded  SAT=25 VIO=0 UNEVAL=0 DENOM=25
R2.patients.sourceId  SAT=4  VIO=0 UNEVAL=0 DENOM=4
R2.cohorts.sourceId  SAT=14 VIO=0 UNEVAL=0 DENOM=14
R2.systemicEvidence.sourceId  SAT=10 VIO=0 UNEVAL=0 DENOM=10
R2.eqPositions.sourceId  SAT=9  VIO=0 UNEVAL=0 DENOM=9
R3.secondary-has-primaryRef  SAT=8 VIO=0 UNEVAL=0 DENOM=8
--- pooled cohorts n=5; context cohorts n=9; total 14
R4.pooled-explicit-integer-counts  SAT=5 VIO=0 UNEVAL=0 DENOM=5
R4b.context-has-contextReason  SAT=9 VIO=0 UNEVAL=0 DENOM=9
R5.pooled-strata-disjoint  SAT=5 VIO=0 UNEVAL=0 DENOM=5  {}
R7.cohort-studyPeriod  SAT=12 VIO=0 UNEVAL=2 DENOM=14
   cohorts[7]:absent-and-not-flagged,cohorts[8]:absent-and-not-flagged
R9.death-partition-coherent  SAT=2 VIO=0 UNEVAL=0 DENOM=2
R10.verified-field-present  SAT=25 VIO=0 UNEVAL=0 DENOM=25  true=25 false=0 missing=[]
--- eq[0] id=rt-localized-emc consensus=contested
    stances=['supports','supports','against','against','against'] bottomLine=yes
```

**V3 — the validator, run read-only.**

```
$ node scripts/validate-registry.mjs
OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).
EXIT=0
$ git status --porcelain | head
(no output)
```

**V4 — identifier guard, `mcp__PubMed__convert_article_ids`, run BEFORE any other retrieval and used for nothing but identifier checking.** Call 1, `id_type="pmid"`, the registry's 16 recorded PMIDs. Verbatim server response:

```
{"status":"ok","response-date":"2026-09-07 23:17:19","request":{"warnings":[],"format":"json","idtype":"pmid","ids":["10366145","35962783","32612944","35144048","18951519","36825763","12599237","31331701","27418251","36568164","33203665","24703573","24345066","27402218","31436747","36948401"],"tool":"pubmed-mcp-server","versions":"no","showaiid":"no"},"records":[{"pmid":"10366145","requested-id":"10366145"},{"pmid":"35962783","requested-id":"35962783"},{"pmcid":"PMC7308468","pmid":"32612944","doi":"10.3389/fonc.2020.00828","requested-id":"32612944"},{"pmid":"35144048","requested-id":"35144048"},{"pmcid":"PMC2779719","pmid":"18951519","doi":"10.1002/cncr.23978","requested-id":"18951519"},{"pmid":"36825763","requested-id":"36825763"},{"pmid":"12599237","requested-id":"12599237"},{"pmid":"31331701","requested-id":"31331701"},{"pmcid":"PMC4946242","pmid":"27418251","doi":"10.1186/s12885-016-2511-y","requested-id":"27418251"},{"pmcid":"PMC9780071","pmid":"36568164","doi":"10.3389/fonc.2022.1042479","requested-id":"36568164"},{"pmcid":"PMC7674086","pmid":"33203665","doi":"10.1136/jitc-2020-001561","requested-id":"33203665"},{"pmid":"24703573","requested-id":"24703573"},{"pmcid":"PMC3879193","pmid":"24345066","doi":"10.1186/2045-3329-3-16","requested-id":"24345066"},{"pmid":"27402218","requested-id":"27402218"},{"pmcid":"PMC7771031","pmid":"31436747","doi":"10.1097/COC.0000000000000590","requested-id":"31436747"},{"pmid":"36948401","requested-id":"36948401"}]}
```

Call 2, `id_type="pmcid"`, the 7 citations that record a PMCID but no PMID. Verbatim:

```
{"status":"ok","response-date":"2026-09-07 23:17:28","request":{"warnings":[],"format":"json","idtype":"pmcid","ids":["PMC12398172","PMC12504171","PMC12863220","PMC12285907","PMC12750061","PMC13136674","PMC7237692"],"tool":"pubmed-mcp-server","versions":"no","showaiid":"no"},"records":[{"pmcid":"PMC12398172","pmid":"40885991","doi":"10.1186/s13018-025-06245-6","requested-id":"PMC12398172"},{"pmcid":"PMC12504171","pmid":"41055792","doi":"10.1007/s00432-025-06316-5","requested-id":"PMC12504171"},{"pmcid":"PMC12863220","pmid":"41635359","doi":"10.7759/cureus.100687","requested-id":"PMC12863220"},{"pmcid":"PMC12285907","pmid":"40704268","doi":"10.7759/cureus.86605","requested-id":"PMC12285907"},{"pmcid":"PMC12750061","pmid":"41476450","doi":"10.3892/ol.2025.15437","requested-id":"PMC12750061"},{"pmcid":"PMC13136674","pmid":"42088406","doi":"10.1155/crip/2779791","requested-id":"PMC13136674"},{"pmcid":"PMC7237692","pmid":"32547189","doi":"10.2147/CMAR.S253201","requested-id":"PMC7237692"}]}
```

**Mismatch check, item by item.** All **23** records have `requested-id` identical to the id I sent (16/16 and 7/7). **Zero mismatches; nothing discarded.** Cross-checking the returned triples against the registry's own recorded fields: **14 citations consistent, 0 mismatched, 11 not checkable by this route** (the converter returned a bare PMID with no PMC/DOI for 9 of them, and 2 citations record only a DOI, which this route does not resolve from). The one apparent difference — `bishop2019` records `10.1097/coc.0000000000000590`, the converter returns `10.1097/COC.0000000000000590` — is DOI letter case, which is not significant, so it is **not** a mismatch. Verbatim summary line from my checker: `GUARD SUMMARY: consistent=14 mismatched=0 not-checked-by-this-route=11 denom=25`.

**No article content was retrieved.** No `get_full_text_article`, no `search_articles`, no `get_article_metadata`, no WebFetch, no WebSearch, no publisher route. **No denied route replayed. No refusals encountered.** $0 spent, no GPU, no paid API.

### PROPOSED (NOT RUN)

- **Retrieving `PMC4946242` to adjudicate F1.** W07f has already shown this reachable at $0 through PubMed MCP. I deliberately did not, because adjudicating the source is a different task from auditing the file, and because the correct repair is a coordinator decision. **The question of which of the two registry fields is right is UNKNOWN from this run.**
- **A `primaryRef` → citation-map cross-check added to `validate-registry.mjs`** to catch F2 automatically (fuzzy surname+year match against citation `authors`/`title`, emitted as a warning). Not written, not tested; would need care against false positives — "Stacchiotti" matches five citation entries, as my §5.4 check showed.
- **Promoting the §2.3 within-study double-counting check from `warns` to `errors`.** Not proposed as an edit, and I did not touch the guard. I only record that the policy's "cardinal sin" is currently a warning.
- **Resolving R6b** (Meis-Kindblom vs USSC/Chiusole overlap) — would require the source's institution list, which is not committed.

## Limitations

1. **Twelve of the twenty-four requirements are not machine-decidable from committed data, and I did not decide them.** R3b (is `sourceId` the document actually read), R7b (was `studyPeriod` taken only from what the source states), R5a (confirmed EMC), and §2.1.4's cross-study overlap all need the sources in hand. A clean row in my table means "conforms on what the bytes can show", never "the extraction is correct".
2. **All 25 citations carry `verified: true` and none carries `false`.** Per the dispatch's own framing, that is 25 claims about past checks, not 25 present verifications — and I performed **zero** of the link-opening checks §1.3 describes. F1 is direct evidence that at least one of those 25 flags sits over an internally contradictory claim. **The `verified` field should be read as unaudited throughout this report.**
3. **The registry's Git history is a single squashed commit**, so I cannot date any field, cannot attribute F1 or F2 to a particular edit, and cannot say which of the two contradicting Morioka fields came first.
4. **HEAD moved under me** (`98a0833f` → `5001d52a`). I verified all five inputs byte-identical across the move, but `W07f`'s tracked/untracked status changed, and I have flagged every place that matters.
5. **My requirement enumeration is a reading, not a specification.** "24 requirements" is my decomposition of the policy prose; a different reader would split §2.1's four conditions or §2.6's eight sub-clauses differently and get a different denominator. The per-row counts are exact; the requirement count is a judgement.
6. **Nothing here is clinical.** This is bookkeeping about a JSON file's conformance to a written contract. It makes no efficacy, safety, prognosis, tolerability or treatment-recommendation claim of any kind, changes no pooled proportion or interval, and says nothing about how any patient with EMC will fare. There is no wet lab and no computational result here at all.
7. **I neither modified nor proposed a modification to the registry**, per the dispatch. F1 and F2 are diagnoses handed to the coordinator, not repairs.

## Stop condition

**Set before the first read:** return as soon as (a) every requirement stated in `POLICY-evidence.md` is enumerated with satisfy/violate/uneval counts and an honest denominator, (b) every violation is named with its row identifier and field, (c) the cross-artifact contradiction question is answered in **both** directions — a contradiction is found and located, or the reconciliation is shown row by row, and (d) `validate-registry.mjs` is read in full and its enforced set separated from its unenforced set; **or** ~40 tool calls / ~40 minutes, whichever comes first.

**Status: MET, on all four, far inside budget.** (a) §5.2, 31 requirement rows plus the two zero-denominator sections. (b) **Zero violations of any decidable requirement** — stated plainly, with denominators, as the dispatch asked; the three findings F1–F3 are named with exact row identifiers and fields and are each characterised as gap or cosmetic rather than inflated into violations. (c) §5.3 finds one real contradiction inside the registry itself, and §5.5 shows the row-by-row reconciliation of everything else, including three independent cross-artifact agreements. (d) §5.6, 9 error-checked / 3 warn-only / 12 unchecked.

## Tool-call and wall-clock count actually used

**Tool calls: 24** — 16 Bash (all read-only repository reads plus one scratch `python3` execution and one read-only `node` validator run), 1 Read (`POLICY-evidence.md`), 1 ToolSearch, 2 PubMed `convert_article_ids`, 4 additional Bash greps folded into the above count. **Wall clock: ~4.2 minutes** (03:14:21 → 03:18:31 UTC, plus final write-up). Well inside the ~40-call / ~40-minute target; returned on stop-condition satisfaction with no padding. Batching the whole field-by-field audit into one scratch script, and both identifier guards into two calls, is what made it cheap.

## Next concrete action

**One coordinator edit, gated on one retrieval: resolve F1 by re-reading `PMC4946242`'s Methods and Table 2 through the PubMed MCP route W07f has already proven reachable at $0, then correct whichever of the two registry fields the source contradicts — and set that citation's `verified` flag to reflect the check actually performed.** The two candidates are `registry.citations.morioka2016trabectedin.population` ("the EMC share of the 5 is not stated") and `treatments.systemicEvidence[6]` ("the full text's Methods state the split"). This is a two-field edit to the registry, it changes **no pooled proportion, no interval, and no cohort row** (the trabectedin row is `n=2`, not a `registry.cohorts` entry, and `meta-analysis.mjs:32` consumes only pooled cohorts), and it must be done by the registry's owner under `POLICY-evidence.md` §1 — **not by me, and not by any worker under this campaign's write isolation.** It should happen before either field is quoted onward, because as committed they cannot both be true.

Subordinate, and explicitly *not* bundled with the above: **F2's four half-repointed secondary rows** are a separate, larger decision — repointing `cohorts[8]` from `remiszewski2025` to `stacchiotti2019pazopanib` means re-reading the phase-2 primary to confirm it supports the exact numbers the row carries, and CLOSED-WORK records that primary's full paper as **unrecovered** (abstract only). So the repoint is **blocked on a source the campaign has not got**, and the row is correct to remain as it is until that changes. I recommend recording that blocker beside the row rather than leaving the half-done state to look like an oversight.
