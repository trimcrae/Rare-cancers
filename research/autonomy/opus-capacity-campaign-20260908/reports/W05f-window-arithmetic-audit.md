> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Audit complete; stop condition met. Report follows.

---

# W05f — Is the temporal-disjointness inference an isolated slip or a pattern?

## Worker

- **Worker:** W05f, LANE 5 refill (cross-study patient independence). Task: tree-wide audit for the inference shape W05e found in one committed file.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`), Claude Code 2.1.42, remote cloud container. I cannot observe the served model; the coordinator must extract the runtime model from the transcript. No environment variable names a model. No finding below depends on which model produced it.
- **`date -u` start:** `Tue Sep  8 02:48:09 UTC 2026`. **`date -u` end:** `Tue Sep  8 02:57:06 UTC 2026`.
- **HEAD actually read — and it moved under me again.** Brief freezes the read commit at `92abbcb905cacf07f14b238db50d1b98f6590374`. At my start `git rev-parse HEAD` returned **`3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`**; at my end **`ce743d6ac63c6645ea65121c7a2157b54b0a2ad8`**. `git status --porcelain` was **empty at start and empty at end**. The coordinator committed twice during my run. As with W05d, **the freeze does not hold**; every file I quote below is a non-campaign research file and my line numbers are from the tree as read between those two commits. The coordinator should re-verify line numbers against the commit it repairs.
- **Write isolation honoured.** Nothing written under `/home/user/Rare-cancers`; all execution under `/tmp/claude-0/w05f/`. No git write operation. **No network egress of any kind** — no PubMed MCP call, no `curl`, no `WebFetch`. This is an audit of committed text only.
- **No patient, case or specimen identity was attempted** (closed-unresolved). No pool, denominator or cohort membership changed. No clinical claim.
- `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — verbatim, with the five proxy-exclusion variables (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy`) elided for length only; they match on the `anthropic` substring inside long host lists and carry no model identity:

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

## Stop condition (declared up front, per dispatch)

**Stop when every tracked `.json`/`.md`/`.py` file has been scanned for the inference shape "patient/case/specimen disjointness asserted from temporal separation alone", every surviving candidate has been classified DEFECTIVE / SOUND / AMBIGUOUS against W05's rubric as written, and each DEFECTIVE row has a survives-on-other-grounds verdict and a routed, unapplied restatement.** — **MET.** Returned immediately on meeting it; no padding.

## Question

**Is the temporal-only disjointness inference W05e found at `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` (cohort `immunosarc1_sts_cohort`) an isolated slip, or a systematic reasoning pattern in the committed corpus?**

Open because W05d measured, by construction over 465 cohort pairs, that "disjoint accrual on a shared time axis alone suffices" is **not** an admissible relaxation of tier B — and the one pair on which it would bite is one the corpus itself flags as a probable overlap. If that same invalid step is written into the corpus in many places, the defect is a rubric-adherence failure across the pooling documents rather than one bad clause; if it appears once, it is a wording bug with a one-line repair. Nothing on record answered which.

**Answer, up front: it is an ISOLATED SLIP, not a pattern.** Across the whole tracked tree, exactly **one** distinct sentence commits the defect. It occurs at **three tracked locations**, but those are one authored sentence plus its two generated copies — a single repair site. Everywhere else the corpus reasons about population overlap on **institution, referral network, authorship, trial registration and containment**, and where it uses time at all it uses it as a *falsifier* (windows overlap → suspect overlap) or explicitly refuses to combine across windows. That is the epistemically correct direction, and the corpus gets it right everywhere except this one clause.

## Prior-work check

Read in full before analysis: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `systems/POLICY-evidence.md` (§2.3, §2.6(d) read verbatim), `reports/W05-patient-independence-audit.md`, `reports/W05b-independence-reconciliation.md`, `reports/W05d-tier-b-conjunctivity.md`. W05's tier rubric is applied **exactly as written and unrelaxed**; I scored nothing under a modified rubric and propose no change to it.

Commands run and what they showed:

| # | command | what it showed |
|---|---|---|
| 1 | `find . -path ./.git -prune -o -name 'W05*' -print` | The three mandated reports live at `research/autonomy/opus-capacity-campaign-20260908/reports/`, not `reports/`. Read there. |
| 2 | `git ls-files research/autonomy/opus-capacity-campaign-20260908/` | The campaign reports **are tracked**, so they are in audit scope; I therefore classify their rubric-quoting lines rather than silently excluding them. |
| 3 | `/tmp/claude-0/w05f/scan.py` (disjointness ∧ temporal lexicon, sentence-level, all tracked `.json/.md/.py`) | 178 hits, dominated by FEP/ABFE false friends (`independent` replicas, lambda `windows`, "therapeutic window"). |
| 4 | `/tmp/claude-0/w05f/scan2.py` (same, plus a mandatory patient/cohort/specimen subject token) | **36 hits, 13 files.** This is the candidate set. |
| 5 | `/tmp/claude-0/w05f/scan3.py` + `filt.py` (5-line sliding window, adds pooling-permission verbs, then keeps only windows where a temporal and a disjointness token sit within 140 characters) | 265 windows → **35 kept**, adding 6 files scan2 missed. No new defective row; all six are SOUND or AMBIGUOUS. |
| 6 | `grep -rn -i 'overlap' --include=*.py` and `grep -rn '"overlap_risk"'` | **No programmatic year-based overlap rule exists anywhere in the corpus.** No validator, pooling script or gate decides overlap from dates. This was the worst case and it is absent. |
| 7 | `grep -rn '"contextReason"' research/data/emc-clinical-registry.json` | All 10 pooling exclusions cite population/institution/endpoint grounds. **None cites a study period.** |

**Closed items I confirm I am not replaying.** No network request of any kind, so no denied route was replayed. I did not touch Brenca, Hofvander/EGA, the restricted NR4A Perspective, paired Davis, promoter transfer, lane-11 source-index material, Sunitinib 2014, Wagner 2020, CTARC 2022, Trabectedin/RT 2018, pazopanib primary, or the anthracycline paper. **I did not re-run W05e's IMMUNOSARC adjudication** — it is settled at tier C → UNKNOWN and I treat that verdict as given, not re-derived. I adjudicated **no new source pair**. I added or removed **no cohort** from any pool or denominator.

## Method / inputs

- Corpus: `/home/user/Rare-cancers`, tracked files only (`git ls-files`), read between `3f5fc95d…` and `ce743d6a…`. `archive/` excluded from the window scan as retired text; it produced no candidate in the sentence scan either.
- File universe: all tracked `.json`, `.md`, `.py`. Non-text and data-only formats not scanned — see Limitations.
- Rubric applied (quoted from `reports/W05-patient-independence-audit.md:125-126`, unmodified): tier **B** = **all three** of disjoint institutions/tissue sources **AND** disjoint accrual windows **AND** disjoint specimen identifier spaces, each individually documented; tier **C** = "any strict subset of tier B's three conditions", licensing **"Nothing on its own … admissible only as a *falsifier*, never as a *confirmer*."**
- Decision rule I applied, stated so it is checkable: a row is **DEFECTIVE** iff the text asserts that patients/cases/specimens *are* disjoint, or *are not* double-counted, and the only ground offered in that assertion is temporal separation. Time cited alongside institution/authorship/registration, or time cited to *raise* an overlap suspicion, is **SOUND**.
- Tools: Python 3 stdlib, offline, three scripts under `/tmp/claude-0/w05f/`, returned inline below. No third-party package.

## Result

### R1 — The defect, in full, at every tracked location `PRIMARY`

One authored sentence. Three tracked occurrences, because the JSON is machine-generated from the Python.

| # | `file:line` | verbatim sentence | class |
|---|---|---|---|
| 1 | `research/manuscripts/emc_systemic_therapy_pooling.py:701` | `"The accrual windows (2017-2019 vs 2020-2024) do not overlap, so the two do not "` `"double-count patients - but a mixed-histology rate cannot enter an EMC pool."` (one string, split across two source lines) | **DEFECTIVE INFERENCE** |
| 2 | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json:577` (`cohorts[].why_excluded`, `immunosarc1_sts_cohort`) | "The accrual windows (2017-2019 vs 2020-2024) do not overlap, so the two do not double-count patients - but a mixed-histology rate cannot enter an EMC pool." | **DEFECTIVE INFERENCE** (generated copy) |
| 3 | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json:1326` (`exclusions_ledger[].explanation`, `immunosarc1_sts_cohort`) | identical sentence | **DEFECTIVE INFERENCE** (generated copy) |

**Repair topology, and it matters:** the JSON's own header carries `_do_not_hand_edit` and `_generated_by`, and `research/manuscripts/emc_systemic_therapy_pooling.py:34` names the output path with `json.dump` at `:1436`. **Rows 2 and 3 must not be hand-edited.** There is exactly **one** repair site — row 1 — and regeneration propagates it to both JSON locations. W05e's dispatch named the JSON; the generator is the file that actually needs the wording change.

**Why it is defective under the rubric as written.** Disjoint accrual is *one* of tier B's three conditions. One of three is, verbatim, tier **C**, which "licenses **nothing on its own**" and is "admissible only as a *falsifier*, never as a *confirmer*." The sentence uses it as a confirmer, and phrases it as a deduction (`so`). Two further facts specific to this pair make it worse, both from committed text and neither requiring any new source:

- The two arms are **stage 1 and stage 2 of one trial registration, NCT03277924** — stated in the same `why_excluded` sentence. Sharing a registration is the opposite of institutional disjointness; tier B's first condition is affirmatively **false** here, so the pair is nowhere near tier B.
- The corpus **separately records the contrary suspicion**: `research/modalities/emc-ipd-survival.json:241` carries `"overlap_risk": "⚠ conference abstract; may be an expansion of martinbroto2020immunosarc1"`, and `:263` carries `"overlap_risk": "⚠ likely the parent trial of immunosarc2emc2025"`. An *expansion* of a cohort contains it. **The repository asserts non-double-counting in one file and flags probable containment in another.** That is an internal inconsistency, not merely a weak inference, and it is the sharpest single reason to repair the wording.

### R2 — Does the conclusion survive? `PRIMARY`

**It survives, cleanly.** This is a wording repair, not a retraction.

`immunosarc1_sts_cohort` is excluded with `pool_orr: false`, `pool_dc: false`, and `pool_reason: "same_registration_as_immunosarc2_and_emc_subset_not_separately_reported"`. The **machine-readable exclusion key names the registration, not the windows** — the defective clause is prose commentary that no pooling decision reads. The operative second ground, stated in the same sentence ("a mixed-histology rate cannot enter an EMC pool"), is independently sufficient: the published 48% is the whole mixed-histology stage-1 cohort and its EMC subset is not separately reported, so the row cannot enter an EMC pool whatever its patient relationship to stage 2. **No denominator, no pooled proportion and no Wilson interval changes under the repair.** Confirmed by reading the record at `:556-577`; I changed nothing.

The residual harm is real but bounded and entirely prose-level: the sentence, as committed, would license a reader to treat IMMUNOSARC I and II as patient-disjoint in some *other* analysis — exactly the transfer the rubric exists to prevent, and exactly the transfer `emc-ipd-survival.json:241` warns against.

### R3 — Everything else the scan found, classified `PRIMARY`

No second DEFECTIVE row exists. The full classified set of substantive candidates:

| `file:line` | what it says (abridged) | class | why |
|---|---|---|---|
| `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json:587` | "The two populations are distinct on every available axis — MSKCC (New York) versus 15 Taiwanese institutions led from Chang Gung Memorial Hospital, no shared authors, no shared referral network" | **SOUND** | A pooling *permission*, and it rests on institution, geography, authorship and referral network. **Time is not invoked at all.** |
| `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json:370` | "CANNOT BE SHOWN NON-OVERLAPPING WITH THE PAZOPANIB TRIAL … (1) Istituto Nazionale Tumori Milan ran this series and was a site of the trial, with the same senior investigator …" | **SOUND** | Exclusion on institution + investigator + entry-criterion argument. Model behaviour. |
| `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json:414` | "CONTAINED IN THE 2014 SERIES … same institution and same investigator. Pooling it would count two responders twice." | **SOUND** | Containment established from the source's own text, not from dates. |
| `research/data/emc-clinical-registry.json:511` | `contextReason: "population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)"`, note "Not pooled to avoid double-counting the US population", with `studyPeriod: [1990, 2016]` adjacent | **SOUND** | The `studyPeriod` field sits beside the exclusion but is not its reason; the reason is registry containment. Adjacency is not inference. |
| `research/modalities/emc-ipd-survival.json` — all 17 `overlap_risk` values, e.g. `:64` "none with institutional series", `:135` "⚠ likely shares Milan/INT patients with the Stacchiotti series", `:383` "⚠ may overlap japan2003 institutions" | **SOUND** | Every one is grounded in registry type, institution, city or trial parentage. **Not one cites a date.** |
| `research/modalities/hormone-partner-lane.json:49,51` and `research/modalities/hormone_partner_map.py:358` | "the two cohorts are treated as NON-OVERLAPPING. That is required by POLICY-evidence and it is NOT VERIFIED here — neither report's accrual institutions were checked." | **SOUND, and exemplary** | Names the assumption as an assumption, names the unperformed check, and states the direction of the resulting bias. This is what the IMMUNOSARC clause should have looked like. |
| `research/manuscripts/no-wet-lab-publication-archetypes.md:471` | "Adjudicate overlap … against study periods **and** institutions … risk: study periods may not disambiguate; some will stay 'cannot exclude overlap' and must be excluded" | **SOUND** | Conjunctive by construction, and it pre-registers the failure mode. |
| `reports/W16c-bishop2019-admissibility-package.md:216` | "`bishop2019` = … 1990-2016 … `ussc2022` = … 2000-2016 … The study windows overlap" | **SOUND** | Time used as a **falsifier**, the one direction tier C permits. |
| `research/modalities/emc-icdo-contamination.json:314`; `systems/graph/routes.json:8367`; `research/manuscripts/care-delivery/emc-icdo-9231-classification.md:283` | "Table 1 of PMID 32856598, as an **independent replication over a different window**" / "as an INDEPENDENT REPLICATION over 1973-2016" | **AMBIGUOUS** | "Independent" here plainly means *a different paper's analysis*, and it supports only a "would sharpen this" wish with no pooling consequence. But it is applied to two SEER pulls that share patients, and the word sits directly on a window. Mitigating and decisive for the classification: the **same file**, at `:307`, says of the neighbouring pair "different overlapping windows … ⛔ THEY STILL MAY NOT BE COMBINED", and `emc-icdo-9231-classification.md:288-292` refuses the cross-window ratio outright ("A ratio spanning two year windows and two registry coverages would look like a measurement and would not be one"). The author's operative reasoning is correct; only the adjective is loose. **Not defective. Flagged for W05's awareness, no repair proposed.** |
| `reports/W05:125`, `W05b:155`, `W05c:174,194,209`, `W05d:68,70,72,143,155,157,247,435`, `W10c:86,187`, `W10d:130,135`, `W01d:132` | rubric text, tier scoring, and W10c's flagged-but-declined relaxation | **SOUND** | These *state* or *test* the conjunctive rule; none applies a temporal-only inference. W10c:187 articulates the relaxation as a hypothesis and explicitly declines to act on it; W05d then measures it and rejects it. Correct process, correctly recorded. |

### R4 — What the absence itself establishes `PRIMARY`

Two negatives are worth as much as the positive finding:

1. **No code anywhere decides overlap from time.** `grep -rn -i 'overlap' --include=*.py` over the whole tree returns no year-comparison, no `studyPeriod` arithmetic, no date-based disjointness predicate in any pooling script, validator or gate. The defect never reached executable logic; it exists only as prose in a generated document's commentary field.
2. **The registry schema offers no temptation.** All 10 `contextReason` values in `emc-clinical-registry.json` and all 17 `overlap_risk` values in `emc-ipd-survival.json` are population/institution-grounded. W05d's finding that the registry has no time-axis field is consistent with this: there is no committed field that a temporal-disjointness rule could even read.

### R5 — Smallest correct restatement, ROUTED AND NOT APPLIED `PREDICTION`

**Routed to: W05 (rubric owner) and the owner of `research/manuscripts/emc_systemic_therapy_pooling.py`. I am read-only and have applied nothing.** Marked `PREDICTION` because it is proposed text whose acceptance is not mine to grant, and because I did not run the generator.

**One repair site**, `research/manuscripts/emc_systemic_therapy_pooling.py:701` (the string continued at `:702`). Replace:

> "The accrual windows (2017-2019 vs 2020-2024) do not overlap, so the two do not double-count patients - but a mixed-histology rate cannot enter an EMC pool."

with the minimal correct form — the observation retained, the deduction removed, the exclusion's real ground promoted:

> "The stated accrual windows (2017-2019 vs 2020-2024) do not overlap, which is one of three conditions for patient-disjointness and does not on its own establish it; the repository separately flags the stage-2 EMC cohort as possibly an expansion of stage 1 (`research/modalities/emc-ipd-survival.json`, `overlap_risk`). Patient overlap between the two stages is UNKNOWN. The exclusion does not depend on it: a mixed-histology rate cannot enter an EMC pool."

Three properties I would ask the owner to check the diff against: (a) the exclusion's operative ground is unchanged and now stated last, in the stress position; (b) the words "do not double-count patients" are gone, so nothing licenses the transfer; (c) UNKNOWN is stated as UNKNOWN, and the contradicting committed flag is cited rather than left to be discovered a third time.

After the edit the generator must be re-run so `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json:577` and `:1326` regenerate; **the JSON must not be hand-edited** (`_do_not_hand_edit`). I did not run it. Whether re-running it perturbs `_generated_utc` or any pinned quantity is **UNKNOWN to me** — I did not execute the script, and `CLAUDE.md §1` requires pinned-quantity changes to be recorded in `research/manuscripts/pinned-figures.json`, which the owner should check before committing.

## Validation evidence

All **RUN**. Environment: `/home/user/Rare-cancers` (reads) and `/tmp/claude-0/w05f/` (execution); Python 3 stdlib, offline; no network.

| # | command | exit | key output |
|---|---|---|---|
| 1 | `date -u; env \| grep …; git rev-parse HEAD; git status --porcelain` | 0 | start `Tue Sep 8 02:48:09 UTC 2026`, HEAD `3f5fc95d…`, status **empty** |
| 2 | `python3 /tmp/claude-0/w05f/scan.py` | 0 | `HITS 178` across 71 files |
| 3 | `python3 /tmp/claude-0/w05f/scan2.py` | 0 | `HITS 36` across 13 files |
| 4 | `python3 /tmp/claude-0/w05f/scan3.py` (backgrounded on 120 s timeout, completed, exit 0) + `python3 filt.py` | 0 | `265` windows → `KEPT 35` |
| 5 | `grep -rn -i 'overlap' --include=*.py .` | 0 | no date-based overlap predicate in any script |
| 6 | `grep -rn '"overlap_risk"' research/modalities/emc_ipd_survival.py research/modalities/emc-ipd-survival.json` | 0 | 32 lines, **zero** citing a date |
| 7 | `grep -rn '"contextReason"' research/data/emc-clinical-registry.json` | 0 | 10 values, **zero** citing a study period |
| 8 | `grep -n -i -E 'json.dump\|OUT_?PATH\|endpoint/emc-systemic-therapy-pooling.json' research/manuscripts/emc_systemic_therapy_pooling.py` | 0 | `34: Output: research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`; `1436: json.dump(doc, fh, indent=1, ensure_ascii=True)` |
| 9 | `python3 -c "import json; print(list(json.load(open(...)).keys()))"` | 0 | `['_schema','_generated_by','_generated_utc','_do_not_hand_edit', …]` — confirms generated, hand-edit-forbidden |
| 10 | `date -u; git rev-parse HEAD; git status --porcelain` (end) | 0 | end `Tue Sep 8 02:57:06 UTC 2026`, HEAD `ce743d6a…`, status **empty** |

The three scripts, returned inline for the coordinator (not written into the tree):

```python
# /tmp/claude-0/w05f/scan2.py  — the candidate-set scan (36 hits)
import re, subprocess, os
os.chdir('/home/user/Rare-cancers')
files=[f for f in subprocess.run(['git','ls-files'],capture_output=True,text=True).stdout.split()
       if f.endswith(('.json','.md','.py'))]
DIS=re.compile(r'(disjoint|non-?overlap|not\s+overlap|no\s+overlap|double[- ]count|independen|'
               r'mutually exclusive|distinct patient|separate patient|shared patient|'
               r'different patient|same patient)',re.I)
TIME=re.compile(r'(accrual|study\s*period|studyPeriod|enrol\w*\s+(window|period)|publication year|'
                r'year of publication|collection date|collected between|calendar|chronolog|temporal|'
                r'19\d\d\s*[-–—]\s*(19|20)\d\d|20\d\d\s*[-–—]\s*20\d\d|\bwindows?\b)',re.I)
SUBJ=re.compile(r'(patient|case\b|cases\b|specimen|cohort|series|registry|population|tumour|tumor|'
                r'enrol|accru|subject)',re.I)
SENT=re.compile(r'[^.!?;]*[.!?;]|[^.!?;]+$')
rows=[]
for f in files:
    try: lines=open(f,encoding='utf-8',errors='replace').read().split('\n')
    except Exception: continue
    for i,line in enumerate(lines,1):
        if len(line)>20000: continue
        if not (DIS.search(line) and TIME.search(line) and SUBJ.search(line)): continue
        for s in SENT.findall(line):
            s=s.strip()
            if s and DIS.search(s) and TIME.search(s) and SUBJ.search(s): rows.append((f,i,s))
print("HITS",len(rows))
for f,i,s in rows: print(f"\n### {f}:{i}\n{s[:900]}")
```

```python
# /tmp/claude-0/w05f/filt.py — proximity filter over scan3.py's 5-line windows (265 -> 35)
import re
txt=open('hits3.txt',encoding='utf-8').read().split('\n### ')
DIS=re.compile(r'(disjoint|non-?overlap|not\s+overlap|no\s+overlap|double[- ]count|mutually exclusive|'
               r'distinct (patient|population|cohort)|shared patient|same patient|may be pooled|'
               r'non-overlapping)',re.I)
TIME=re.compile(r'(accrual|study\s*period|studyPeriod|enrol\w*\s+(window|period)|collection date|'
                r'collected between|19\d\d\s*[-–—]\s*(19|20)\d\d|20\d\d\s*[-–—]\s*20\d\d|'
                r'different window|later|earlier|predat)',re.I)
out=0
for blk in txt[1:]:
    flat=' '.join(blk.split())
    ds=[m.start() for m in DIS.finditer(flat)]; ts=[m.start() for m in TIME.finditer(flat)]
    if any(abs(d-t)<=140 for d in ds for t in ts):
        out+=1; print('### '+flat[:520]+'\n')
print('KEPT',out)
```

(`scan3.py` differs from `scan2.py` only in scanning 5-line sliding windows, adding `may be pooled|pool(ed|able)?` to `DIS`, and excluding `archive/`.)

## Limitations

1. **Lexical recall is not proof of absence.** The scan finds the defect where it is written in recognisable words. A temporal-only disjointness inference phrased entirely outside my lexicon — say, a table whose "independent?" column is populated purely from a years column with no sentence anywhere — would be missed. `PROPOSED (NOT RUN)`: a schema-level pass asserting that no independence-bearing field's value is a pure function of date fields. **"One defect found" is a floor, not a certified ceiling.**
2. **Scope is `.json`/`.md`/`.py` only.** CSV, TSV, notebooks, YAML and any binary or non-text artifact were not scanned. Their content is **UNKNOWN**, not clean.
3. **The freeze did not hold** (HEAD `3f5fc95d…` → `ce743d6a…` during the run). No file I quote is a campaign file and the tree was clean at both ends, so I have no evidence any quoted line moved; but line numbers should be re-verified against the commit that receives the repair.
4. **`archive/` was excluded from the window scan** as retired text. It produced no candidate in the broader sentence scan, but I did not audit it deliberately.
5. **The restatement is unapplied, unexecuted and unreviewed.** I did not edit any file, did not run the generator, and did not run `scripts/preflight.sh` (the brief forbids it absent a dispatch instruction). Whether regeneration is byte-clean apart from the intended sentence is **UNKNOWN**.
6. **No source was retrieved and no pair was adjudicated.** Every classification above rests on committed text as written. In particular I did **not** re-open IMMUNOSARC: W05e's tier C → UNKNOWN is taken as given, and the `emc-ipd-survival.json` overlap flags are quoted as committed repository statements, not re-verified against their sources.
7. **No clinical claim.** Nothing here bears on EMC treatment, efficacy, safety or prognosis; the corrected sentence removes an unsupported epistemic claim and changes no number a clinician or patient would read.
8. **I hold no authority over the rubric** and propose no change to it. W05d's measured verdict — the conjunctivity is load-bearing — is the input to this audit, not something I re-litigated.

## Tool-call and wall-clock count actually used

**17 tool calls** (16 `Bash`, 1 background-wait), against the ~40 target. **Wall clock 8 min 57 s** (`02:48:09Z` → `02:57:06Z`), against the ~40 min target. Returned on meeting the stop condition rather than spending the remaining budget.

## Next concrete action

**One task, and it is a repair rather than an investigation: hand `research/manuscripts/emc_systemic_therapy_pooling.py:701-702` to its owner with the R5 replacement string, re-run the generator, and diff `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` to confirm the only content change is at `:577` and `:1326`.** It is a single-site, zero-denominator-impact wording fix whose correctness is fully established by committed text (the trial registration is in the sentence itself; the contradicting `overlap_risk` flag is in `emc-ipd-survival.json:241`), it needs no source retrieval, and it closes the one place in the corpus where the repository asserts patient non-double-counting on a ground its own rubric says licenses nothing.

Two lower-value successors, named so they are not lost: (a) the schema-level check in Limitation 1, which would convert "one defect found" into a bounded ceiling; (b) an optional wording touch-up of the three "independent replication over a different window" strings (R3, AMBIGUOUS) — I would **not** spend a lane on it, since the operative reasoning in those files is already correct and explicitly refuses the cross-window combination.

---

result: Audited the whole tracked tree (all `.json`/`.md`/`.py`, three scans, 178 → 36 → 35 candidates) for "patient/case/specimen disjointness inferred from temporal separation alone" and found it is an **ISOLATED SLIP, not a pattern** — exactly one authored sentence commits the defect, at one repair site (`research/manuscripts/emc_systemic_therapy_pooling.py:701`) plus its two machine-generated copies (`research/manuscripts/endpoint/emc-systemic-therapy-pooling.json:577` and `:1326`, a file marked `_do_not_hand_edit`, so W05e's named JSON is not the file to edit); the conclusion it supports **survives on other grounds** (the exclusion's machine-readable `pool_reason` names the shared NCT03277924 registration, and the mixed-histology bar is independently sufficient — no denominator, pooled proportion or Wilson interval moves), so this needs a wording repair and not a retraction; the defect is sharpened by an internal inconsistency the audit surfaced, `research/modalities/emc-ipd-survival.json:241` flagging the stage-2 cohort as "may be an expansion of martinbroto2020immunosarc1", i.e. probable containment asserted in one file against non-double-counting asserted in another; everywhere else the corpus is sound — all 17 `overlap_risk` values and all 10 registry `contextReason` values ground overlap in institution/registry/authorship and **not one cites a date**, no pooling script, validator or gate contains any date-based overlap predicate, and where time appears it is used as a falsifier (W16c) or the cross-window combination is explicitly refused (`emc-icdo-contamination.json`); three "independent replication over a different window" strings classified AMBIGUOUS with no repair proposed; smallest correct restatement given, routed to W05 and the file owner and **not applied**; read-only honoured (`git status --porcelain` empty at start and end), no network, no new pair adjudicated, no cohort added or removed, HEAD moved `3f5fc95d…`→`ce743d6a…` under me and is reported not smoothed; 17 tool calls, 8 min 57 s.
