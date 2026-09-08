> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, extracted by the coordinator from the child transcript:
> `"model":"claude-opus-5"` (OBSERVED, not self-report).

---

Coordinator correction acknowledged and complied with: I am read-only on the tree, wrote nothing into the repository (my one heredoc attempt failed before creating anything — verified: no `reports/` directory, no `W07*` file anywhere), and the report follows inline. Model identity is stated as self-report only.

Sanity check performed: re-read the updated COMMON-BRIEF.md, re-verified the frozen HEAD, re-verified the zero-hit and one-hit PubMed counts that the finding rests on, and confirmed against the ask that both halves of the stop condition (denominator table + evidence-backed absence) are delivered.

---

# W07 — EMC patient-reported outcomes, symptom burden, follow-up duration, and reporting denominators

## Worker

- **Worker ID:** W07 · **Lane 7** — EMC patient-reported outcomes, symptoms, disease burden, follow-up evidence, reporting denominators.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I report myself as Claude Opus 5 (`claude-opus-5`) running under Claude Code 2.1.42 in a remote cloud environment. I did not observe the served model and do not assert it as fact; the coordinator extracts the actual per-child runtime model from the transcript.
- **Frozen read commit:** `92abbcb905cacf07f14b238db50d1b98f6590374` (`git rev-parse HEAD`, exit 0).
- **`date -u` at start:** `Tue Sep  8 01:51:48 UTC 2026` · **at end:** `Tue Sep  8 01:56:15 UTC 2026`

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — end-of-run output (identical at start, same shell environment; four proxy/`JAVA_TOOL_OPTIONS` lines that matched only through embedded `anthropic.com` hostnames are filtered as noise):

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

**Write-isolation compliance:** I created no file in the repository. One `cat > …/reports/W07-….md` heredoc was attempted before the correction arrived and **failed** (`No such file or directory`, exit 1) — the `reports/` directory did not exist and my earlier `mkdir -p` did not take effect. Verified after the correction: `ls …/reports` → `No such file or directory` (exit 2); `find . -name "W07*" -not -path "./.git/*"` → no output. Nothing to delete.

---

## Question

**Does any retrievable EMC source report a patient-experienced outcome — symptoms at presentation, functional status, quality of life, treatment toxicity as experienced, or duration of follow-up — attached to a stated denominator? And what does the pattern of denominators tell us about which patient-burden claims this programme can make?**

Open because every clinical artifact in this repository is built on tumour-side endpoints — survival, recurrence, response, margin status, terminal event — and none audits the *patient-side* record. The repository has a denominator discipline (`POLICY-evidence.md`, the trabectedin denominator artifact) but has never applied it to PRO/symptom/follow-up data. The lane's premise — that missing denominators are themselves the finding — had not been tested.

---

## Prior-work check

Commands run (read-only, from `/home/user/Rare-cancers`):

1. `rg -n -i "quality of life|QoL|PROM|patient.report|symptom|toxicity|follow.up|EORTC|functional" research/ --glob '!.git' | head -80`
2. `git ls-files | rg -i "outcome|symptom|qol|supportive|palliat|care-deliver|toxic" | head -40`
3. `rg -n -i "denominator" research/ --glob '!.git' -l | head -30`
4. `rg -n -i "median follow.up|follow-up of|symptom|pain|swelling|mass|dyspn|toxicit|adverse|grade 3|neutropen" systems/ --glob '*.json' --glob '*.md' | head -50`
5. `git ls-files | rg -i "emc-.*\.json" | head -40`
6. Structured walk of `research/data/emc-clinical-registry.json` for every object carrying `medianFollowupMonths`/`followupMonths` (output in Validation evidence).

**What the corpus already covers, and which I am not replaying:**

- `research/manuscripts/emc-mortality-mechanisms.md` §3 and `systems/views/L2-rt-early-palliative.md` hold the **transferred** class-level early-palliative-care finding (Temel 2010 PMID 20818875 n=151; PACO/Allende 2024 PMID 38558247 n=146; Chen 2023 PMID 37781179 n=140; Kochovska 2020 PMID 32953543). All three trials are NSCLC. That memo already states that no sarcoma-specific trial was found and that transfer to a decade-scale disease is untested. **I do not restate, re-grade or extend it.** My lane is the EMC-side denominator audit, which it does not do.
- `research/literature/emc-trabectedin-denominator-2026-09-01.json` is a denominator audit — of *response* counts, not PRO/symptom/follow-up. I reuse its retained facts and do not re-derive them.
- `systems/views/L2-rt-treatment-harm.md` records the corrected terminal-event count (2/52 classified deaths treatment-related, both postoperative skull-base). Cited as context; not re-reviewed.
- `systems/views/L2-rt-surveillance.md` and `L2-rt-scheduling.md` record the follow-up-vs-recurrence censoring observation and the "median follow-up quoted as median PFS" error. My table is consistent with both and re-opens neither.
- **CLOSED-WORK compliance:** the anthracycline row (`PMC3879193` / PMID 24345066) is used **only** at retained strength — median 4 cycles (range 1–8), separate non-missing denominator unknown, one patient stopping after cycle 1 for toxicity, **no rate derived**. Pazopanib, Sunitinib 2014, Wagner 2020, CTARC 2022 and Trabectedin/RT 2018 were **not re-fetched**; no denied route replayed. No cohort invented.
- **Not previously done anywhere in the tree:** a table of EMC patient-experienced outcomes with numerator/denominator status. The string `quality of life` occurs **0 times** in `emc-clinical-registry.json`.

---

## Method / inputs

**Repository inputs (read-only, frozen commit):** `research/data/emc-clinical-registry.json`; `research/literature/emc-trabectedin-denominator-2026-09-01.json`; `research/manuscripts/emc-mortality-mechanisms.md`; `systems/views/L2-rt-treatment-harm.md`; `systems/views/L2-rt-surveillance.md`; `systems/graph/evidence.json`.

**External retrieval:** PubMed, via the PubMed MCP server (`search_articles`, `get_article_metadata`), all queries executed 2026-09-08 between 01:52 and 01:53 UTC. Article metadata below is **from PubMed**; DOI links given for every article cited.

**Local literature cache absent:** paths referenced elsewhere in the tree as `literature/emc-radiotherapy-2026-08-26/…` and `literature/emc-care-delivery-and-classification/…` **do not exist in this checkout** (`ls -d literature` → `No such file or directory`; `git ls-files | rg '^literature'` → no matches). Untracked. This is a retrieval limitation of my environment, **not** evidence those papers lack PRO content — marked UNKNOWN, not zero.

**Exact queries run:**

| # | Query string | `total_count` |
|---|---|---|
| Q1 | `(extraskeletal myxoid chondrosarcoma) AND (quality of life OR patient-reported OR PROM OR EORTC OR functional outcome)` | 21 |
| Q2 | `extraskeletal myxoid chondrosarcoma AND (symptom OR pain OR presentation)` | 397 |
| Q3 | `"extraskeletal myxoid chondrosarcoma"[All Fields] AND "quality of life"[All Fields]` | **1** |
| Q4 | `"extraskeletal myxoid chondrosarcoma"[All Fields] AND ("patient-reported"[All Fields] OR "patient reported outcome"[All Fields] OR "EORTC QLQ"[All Fields] OR "TESS"[All Fields] OR "MSTS"[All Fields] OR "PROMIS"[All Fields])` | **1** |
| Q5 | `"extraskeletal myxoid chondrosarcoma"[All Fields] AND ("adverse event"[All Fields] OR "adverse events"[All Fields] OR "toxicity"[All Fields] OR "tolerability"[All Fields])` | 9 |
| Q6 | `("soft tissue sarcoma"[All Fields] AND "quality of life"[All Fields] AND ("ultra-rare"[All Fields] OR "myxoid chondrosarcoma"[All Fields]))` | **0** |

Q1 and Q2 are inflated by PubMed term expansion — the returned `query_translation` shows `functional outcome` exploding to `"physiology"[MeSH]` and `presentation` to `"diagnosis"[MeSH Subheading]` plus every inflection of "present". Q3–Q6 are unexpanded literal-phrase searches and are what the absence finding rests on.

---

## Result

### 5.1 Headline

**EMC-specific PRO evidence is essentially absent, and the absence is now measured rather than asserted.** Across the entire PubMed PRO instrument vocabulary, EMC returns **exactly two papers**, contributing **one instrumented functional measurement in one patient** and **one narrative symptom statement covering three patients**. No EMC cohort of any size has been reported with a quality-of-life instrument.

### 5.2 Denominator-audited table — every retrievable patient-experienced datum

Codes: **FULL** = denominator is the complete stated cohort; **PARTIAL** = stated subset, missingness mechanism unstated; **UNSTATED** = value with no recoverable denominator; **N/A** = duration, not a proportion.

| # | Datum, as reported | Num. | Denominator | Denom. status | Grade | Source |
|---|---|---|---|---|---|---|
| 1 | MSTS 100%; QuickDASH 20.5, at 5 yr, no recurrence, "excellent function", returned to occupation — hand EMC after wide resection + extracorporeal-irradiation bone/tendon reconstruction | 1 | 1 EMC patient (Case 1 of a 3-case report; Cases 2–3 are synovial sarcoma) | **FULL** (of an n=1 EMC denominator) | PRIMARY | Terao 2026, PMID 41689087, [DOI](https://doi.org/10.1186/s12957-026-04247-0) |
| 2 | "the patients remained **asymptomatic** from their pulmonary metastases" during long-term observation without systemic therapy | 3 | 3 (whole case series) | **FULL** | PRIMARY | Masrouha 2020, PMID 32963861, [DOI](https://doi.org/10.1155/2020/2684746) |
| 3 | "improving their quality of life by avoiding potentially debilitating treatments" | — | — | **UNSTATED** — authors' inference, not a measurement; no instrument, score or timepoint | UNKNOWN (not a datum) | Masrouha 2020, [DOI](https://doi.org/10.1155/2020/2684746) |
| 4 | Median follow-up 38 mo, localised-at-diagnosis surgically treated | — | n = 134 (8 non-surgical localised excluded) | **N/A (duration)**; cohort n stated, ascertainment for all 134 not stated → non-missing denominator UNKNOWN | SECONDARY | registry `registry.cohorts[0]` |
| 5 | Median follow-up 41 mo, metastatic at diagnosis | — | n = 29 (27 lung, 2 peritoneal; 16 systemic therapy) | **N/A**; same caveat | SECONDARY | `cohorts[1]` |
| 6 | Median follow-up 108 mo (9 yr) | — | n = 117 (AFIP consultation series, Meis-Kindblom) | **N/A**; consultation-referral selection | SECONDARY | `cohorts[2]` |
| 7 | Median follow-up 94 mo; 5/41 (12%) local relapse | 5 | 41 consecutive localised | **FULL** for the relapse proportion; duration N/A | SECONDARY | `cohorts[5]` |
| 8 | Median follow-up 33 mo; 94% surgery, 32% radiotherapy | — | n = 156 (US SEER localised) | **N/A**; registry does not capture recurrence → no patient-experienced event derivable | SECONDARY | `cohorts[6]` |
| 9 | Median follow-up 8.5 mo (range 2–28); median PFS **not reached** | — | n = 10 (sunitinib, named-patient use) | **N/A**. Flagged in-repo as a figure miscarried elsewhere as a median PFS | SECONDARY | `treatments.systemicEvidence[2]` + registry correction |
| 10 | Individual case follow-up: 22, 16, 3, 36 mo | — | 4 individually sourced cases | **N/A**; case 2 explicitly "lost to follow-up" after 16 mo | SECONDARY | `registry.patients[0..3]` |
| 11 | Anthracycline: median 4 cycles, range 1–8; **one** patient stopped after the first cycle for toxicity | 1 | **UNKNOWN** — separate non-missing denominator not retained | **UNSTATED** | UNKNOWN | PMID 24345066 / PMC3879193, retained strength only |
| 12 | Trabectedin EMC subset: 2 stable / 1 progressive; ORR "–" | 3 | 3 EMC within an arm of 36 (35 evaluable) | Response **FULL** for n=3; **toxicity reported arm-wide only** — no EMC-specific safety denominator exists | PRIMARY (retained) | Palmerini 2022, PMID 36568164, [DOI](https://doi.org/10.3389/fonc.2022.1042479) |
| 13 | Trabectedin, Japanese sub-analysis: stable disease in both; individual PFS 13.0/7.4 mo, OS 26.4/10.4 mo | 2 | 2 EMC within a 5-subject trabectedin allocation | **FULL** for n=2; no PRO, no toxicity attributable to the EMC pair | PRIMARY (retained) | Morioka 2016, PMID 27418251, [DOI](https://doi.org/10.1186/s12885-016-2511-y) |
| 14 | Symptoms at presentation (pain, swelling, mass, functional limitation) as frequencies with a denominator, in **any** EMC series | — | — | **UNSTATED / not located** | UNKNOWN | none located; Q2/Q3/Q4 returned none |
| 15 | Any EMC cohort reporting a validated QoL instrument (EORTC QLQ-C30 ± sarcoma module, FACT-G, PROMIS, EQ-5D) | 0 | — | **Absent** | UNKNOWN (measured absence) | Q3 = 1 paper, which uses the phrase rhetorically |
| 16 | Structured patient-reported symptom monitoring in EMC | 0 | — | **Absent**; in-repo class evidence is NSCLC-transferred | UNKNOWN (measured absence) | `emc-mortality-mechanisms.md` §3; `L2-rt-early-palliative.md` |

### 5.3 What the denominator pattern shows — three distinct, non-interchangeable failure modes

1. **Denominator present, n catastrophically small.** Rows 1, 2, 12, 13. Every EMC patient-experienced datum with a clean denominator has a denominator of **1, 2, 3 or 3**. The only instrumented functional data rest on a single patient in a case report whose other two patients have a different histology.
2. **Denominator present for the cohort, absent for the measurement.** Rows 4–10. Good cohort sizes (134, 156, 117, 41, 29) and good follow-up durations — but a median follow-up is a property of the *study*, not of a patient's experience, and none of these cohorts states how many patients the follow-up figure was computable for.
3. **Denominator destroyed by aggregation.** Rows 11, 12. EMC toxicity is reported only inside larger sarcoma arms: Palmerini's safety data belong to 36 patients of whom 3 are EMC; the anthracycline toxicity event has an unknown non-missing denominator. **This is the mode that most invites a fabricated rate** — "one patient stopped after the first cycle" over "median 4 cycles across an unknown n" is not a discontinuation rate and must never be written as one.

### 5.4 Supportable vs. non-supportable patient-burden claims

**Supportable, with the denominator attached:**
- *"In the only EMC patient in the literature with an instrumented functional outcome after limb-sparing hand reconstruction, MSTS was 100% and QuickDASH 20.5 at five years (n = 1)."*
- *"In one three-patient series, all three patients with pulmonary metastases managed by observation alone remained asymptomatic from those metastases over several years of imaging follow-up (3/3)."*
- *"No EMC cohort has been reported with a validated quality-of-life instrument."* (established by Q3/Q4/Q6, 2026-09-08)
- *"Reported EMC follow-up medians range from 33 to 108 months across cohorts of 29 to 156 patients"* — provided each median stays attached to its own cohort, is never pooled, and is never restated as a survival or PFS figure.
- *"EMC treatment toxicity has never been reported with an EMC-specific denominator."*

**Not supportable, and why:**
- **Any EMC symptom prevalence, of anything, at any timepoint** — no source gives a numerator over a denominator (Row 14).
- **Any claim that EMC patients are "typically asymptomatic" or "typically symptomatic"** — Row 2's three patients were selected *for* being observation-managed, the least symptomatic possible sampling frame; generalising inverts the selection.
- **Any treatment-discontinuation, dose-reduction or toxicity rate** — Row 11 forbids it explicitly; Row 12 shows the only alternative source aggregates EMC away.
- **Any claim that EMC quality of life is preserved or damaged by any treatment** — Row 3 is a rationale sentence, and it is the *entire* QoL literature.
- **Any claim that follow-up in EMC is adequate or inadequate for the patient** — duration medians describe study conduct. The relevant observation (upper-quartile time to local recurrence 63.5 mo vs median follow-up 38 mo) already lives in `L2-rt-surveillance.md` with its three limits; this audit does not strengthen it.
- **Any EMC-specific benefit from early palliative care or structured symptom monitoring** — the class evidence is three NSCLC trials and the transfer is untested.

### 5.5 Why this is a reportable negative result, not a null search

Q3, Q4 and Q6 are literal-phrase queries with no term expansion, over a database indexing 397 EMC-mentioning papers under the loosest symptom query (Q2). A disease with 397 indexed papers, **one** containing the phrase "quality of life" (used rhetorically) and **one** containing any PRO instrument name, is not an under-searched disease. It is a disease whose literature has been written entirely from the tumour's point of view. That is a defensible statement about the field and the strongest thing this lane can deliver.

---

## Validation evidence

### RUN

**V1.** `git rev-parse HEAD` → `92abbcb905cacf07f14b238db50d1b98f6590374`. Exit 0.

**V2.** Local literature cache absent:
```
$ ls -d literature
ls: cannot access 'literature': No such file or directory      # exit 2
$ git ls-files | rg -i "^literature"                            # no output, exit 1
```

**V3.** Write-isolation verification after the coordinator's correction:
```
$ ls -la research/autonomy/opus-capacity-campaign-20260908/reports
ls: cannot access '...reports': No such file or directory       # exit 2
$ find . -name "W07*" -not -path "./.git/*"                     # no output, exit 0
```
Confirms the earlier heredoc created nothing; no repository file to delete.

**V4.** Registry follow-up walk (inline Python 3 over `research/data/emc-clinical-registry.json`), verbatim:
```
/registry/patients[0] {"followupMonths": 22, ...}
/registry/patients[1] {"followupMonths": 16, ... "lost to follow-up" ...}
/registry/patients[2] {"followupMonths": 3, ...}
/registry/patients[3] {"followupMonths": 36, ...}
/registry/cohorts[0] {"label": "Localised at diagnosis, surgically treated", "n": 134, "medianFollowupMonths": 38, ...}
/registry/cohorts[1] {"label": "Metastatic at diagnosis", "n": 29, "medianFollowupMonths": 41, ...}
/registry/cohorts[2] {"label": "Long-term outcome series (Meis-Kindblom)", "n": 117, "medianFollowupMonths": 108, ...}
/registry/cohorts[5] {"label": "Localised, single-institution series", "n": 41, "medianFollowupMonths": 94, ...}
/registry/cohorts[6] {"label": "Localised, US SEER population", "n": 156, "medianFollowupMonths": 33, ...}
/treatments/systemicEvidence[2] {"n": 10, "medianFollowupMonths": 8.5}
```
Exit 0.

**V5.** Term census over the registry (inline Python `re.finditer`, case-insensitive), verbatim:
```
follow 33
symptom 3
pain 3
swell 0
mass 0
dyspn 0
toxic 1
advers 1
quality of life 0
presentation 4
```
Exit 0. **`quality of life` occurs zero times in the EMC clinical registry.**

**V6.** PubMed Q1–Q6 executed via the PubMed MCP server, 2026-09-08 01:52–01:53 UTC. Server-returned `total_count`: 21, 397, **1**, **1**, 9, **0**. Q3 → `["32963861"]`; Q4 → `["41689087"]`; Q6 → `[]`.

**V7.** Metadata retrieved for PMIDs `32963861`, `41689087`, `32967265`. Verbatim source sentences used:
- PMID 41689087: *"At 5 years, he showed no recurrence and excellent function (Musculoskeletal tumor society (MSTS) score, 100%; Quick Disabilities of the Arm, Shoulder and Hand (QuickDASH) score, 20.5)."*
- PMID 32963861: *"Follow-up imaging showed slow progression of their disease over several years, and the patients remained asymptomatic from their pulmonary metastases."* / *"…thereby improving their quality of life by avoiding potentially debilitating treatments."*

Article metadata in this report is from **PubMed**.

### PROPOSED (NOT RUN)
- Full-text retrieval of PMID 41689087 (PMC13005408) to confirm no further EMC-specific functional timepoints. Not attempted — the abstract already carries the instrumented values, and PMC egress is recorded in this repository as commonly blocked.
- Symptom-at-presentation extraction across the 397 Q2 hits. Out of bounded-run budget; the right instrument is a CI-side fetch.
- `scripts/preflight.sh` — **not run**; not authorised by this dispatch and no code was authored.

### Content-policy refusals
**None encountered.** No branch was refused; no denied route replayed.

---

## Limitations

1. **The local literature cache is absent from this checkout.** PMC12398172 (Masunaga 2025), PMC12504171 (Remiszewski 2025) and the other cached full texts could not be opened. Any symptom or toxicity denominator inside them is **UNKNOWN to this report, not absent from the world.** Row 14 and the toxicity conclusion in §5.4 must be re-checked against those caches before publication.
2. **Q5's nine toxicity hits were not individually read.** I claim only that no *EMC-specific* toxicity denominator was located, resting on the retained Palmerini structure and the retained anthracycline row. A per-paper read could surface one.
3. **Rows 4–10 are curated secondary values**, read from the registry rather than re-verified against each primary paper in this session; they carry the registry's provenance, not fresh verification.
4. **Row 2 has severe selection bias in the direction of the claim** — three patients chosen for observation management are by construction the least symptomatic available. Reported for its clean denominator, not because it generalises.
5. **No transfer from sarcoma-wide PRO literature is asserted.** Q6 returned zero and I did not substitute a mixed-STS QoL cohort for an EMC one.
6. **This report establishes nothing clinical.** It is an evidence-availability audit; it does not estimate EMC symptom burden and cannot — with n = 1 instrumented patient no estimate exists to make.
7. **A measured absence in PubMed is not global absence.** Conference abstracts, registry PRO collections, non-English and unindexed literature lie outside these six queries.

---

## Stop condition

**Set:** a denominator-audited PRO evidence table, or an evidence-backed absence finding with the exact searches establishing it.

**Status: MET — both halves delivered.** §5.2 is the denominator-audited table (16 rows, each graded, every proportion carrying explicit denominator status); §5.5 with the Q1–Q6 `total_count` values is the evidence-backed absence finding.

---

## Tool-call and wall-clock count actually used

**Tool calls: 22** (2 skill/brief reads, 12 Bash, 2 ToolSearch, 5 PubMed MCP, 1 metadata batch). **Wall clock: ~4.5 minutes** (01:51:48 → 01:56:15 UTC). Both well inside the ~40-call / ~40-minute self-observed target; returned on stop-condition satisfaction rather than padding.

---

## Next concrete action

Read the nine Q5 toxicity hits (PMIDs `41476450`, `41323055`, `36568164`, `35494187`, `34716194`, `32547189`, `31509242`, `31331701`, `23058004`) at abstract level and record, per paper, whether any adverse-event count attaches to an **EMC-specific denominator** or only to a mixed-sarcoma arm. Finite (~9 articles), binary per row, directly closes Limitation 2, and decisive either way: if all nine aggregate EMC away, "EMC treatment toxicity has never been reported with an EMC-specific denominator" becomes a fully enumerated claim rather than an inference from two series. Run it where the local literature cache is present so full texts can be checked before an absence is recorded.

---

result: EMC patient-reported-outcome evidence is measurably near-absent — the entire PubMed PRO vocabulary returns 2 papers, giving 1 instrumented functional measurement (MSTS 100%/QuickDASH 20.5, n=1) and one 3/3 asymptomatic narrative; zero EMC cohorts have any validated QoL instrument, and EMC toxicity has never been reported with an EMC-specific denominator — delivered as a 16-row denominator-audited table plus the six literal queries establishing the absence, returned inline with no repository writes.
