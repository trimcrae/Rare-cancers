> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, extracted by the coordinator from the child transcript:
> `"model":"claude-opus-5"` (OBSERVED, not self-report).

---

Sanity check: `git rev-parse HEAD` = `92abbcb905cacf07f14b238db50d1b98f6590374` (the frozen commit), and `git status --porcelain` shows only the pre-existing untracked campaign directory — I created and modified nothing in the tree. Report follows in this response body per the correction.

---

## Worker

- **Worker:** W09, LANE 9 — EMC care-access and referral questions with identifiable public data.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). I did not and cannot observe the served model from inside this session; the coordinator should extract the actual runtime model from the transcript. `env` exposes no model variable (see below) — `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions, not model identities.
- **Write isolation:** received the coordinator's read-only correction mid-run. I had written **no** files at any point; nothing to delete. `git status --porcelain` at start and end shows only `?? research/autonomy/opus-capacity-campaign-20260908/` — the coordinator's own pre-existing untracked brief directory.

`date -u` at start of environment capture and at end (single capture, run once, 2026-09-08T01:54:19Z):

```
Tue Sep  8 01:54:19 UTC 2026
```

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0), model-relevant lines; long proxy `no_proxy`/`JAVA_TOOL_OPTIONS` lines elided as marked, nothing else removed:

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
[elided: no_proxy, NO_PROXY, GLOBAL_AGENT_NO_PROXY, npm_config_noproxy, JAVA_TOOL_OPTIONS — proxy host lists, no model information]
```

⛔ **No environment variable names a model.** My model self-report above therefore rests on nothing checkable from inside this container.

## Question

**Which public, identifiable data sources actually record where an EMC patient was treated (specialist sarcoma centre vs general centre), and is EMC *separately reportable* in any of their public outputs?**

Why it was open when I started: the repository had closed the *published-series* half of this question (`emc-surgical-quality.json` → `treatment_setting.recorded_in_any_reachable_series: false`) and had separately closed NCDB on structural grounds, but it had **not** assembled a source-by-source identifiability audit, and it carried at least one explicitly `UNVERIFIED` identifiability claim (RARECAREnet) plus an open route unknown ("whether facility volume is recoverable at all in the public files") that was answered for only one of several candidate sources.

⛔ **Hard exclusion honoured.** Nothing below calibrates EMC values from generic SEER parameters, asserts a plausible-EMC quantity, or asserts an age gradient. This report is entirely about *whether a variable is separately reportable*, which is a different question from calibration and does not license one.

## Prior-work check

Commands actually run, in order:

1. `rg -n -i "referral|centre|center volume|access|specialist|sarcoma centre|equity|travel|insurance" research/ --glob '!.git' | head -80` — returned mostly open-access/publication-fee noise (the word "access"), plus two on-target hits: `research/manuscripts/dependency/emc-sgk1-lane-assessment.md:114` (PMID 18951519, "EMC retrospective clinical review, 2 referral centres") and `research/manuscripts/emc-mortality-mechanisms.md:247` (Drilon 2008 two-referral-centre series, n = 87).
2. `ls -la research/manuscripts/care-delivery/` + `git ls-files | rg -i "care-delivery|referral|access"` — 9 records in `care-delivery/`, 2300 lines total; also `research/modalities/emc-care-delivery-evidence.json` and `systems/views/L1-st-care-delivery.md`.
3. Read in full: `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md` (464 lines, all sections).
4. `python3` field-walk over `research/modalities/emc-surgical-quality.json`, grepped for `setting|centre|center|referral|unplanned|specialist`.
5. `python3` field-walk over `research/manuscripts/care-delivery/icdo-9231-restriction-audit.json`.
6. `rg -n -i "NCDB|National Cancer Database|RARECARE|NETSARC|EURACAN|reference network|Commission on Cancer|facility|Get Data Out|NCRAS|sarcoma audit|hospital volume" --glob '!.git' -l` and the same as a content grep.
7. `sed -n` reads of `research/manuscripts/no-wet-lab-publication-archetypes.md` §4.4, §6.3, §6.4 and `research/literature/no-wet-lab-archetypes-2026-08-12.json`.

**Closed items I confirmed and am NOT replaying:**

| Closed item | Where it lives | I did not replay it |
|---|---|---|
| Treatment setting absent in both curated EMC series (Masunaga 2025 prints no centre; Chiusole 2020 is 100 % referral-centre care, exposure constant by construction) | `research/modalities/emc-surgical-quality.json` → `treatment_setting` | Confirmed by reading; did not re-curate either paper |
| Unplanned excision not recorded as a rate in either series; both candidate proxies `is_the_thing: false` | same file → `unplanned_excision` | Confirmed; see §Result row R7 for a **narrowing**, not a replay |
| NCDB PUF cannot answer facility volume — the PUF identifies neither patients, providers nor hospitals | `no-wet-lab-publication-archetypes.md` §4.4 item 2 | Adopted as SECONDARY; did not re-derive |
| NCDB PUF access structurally closed (CoC affiliation + insider designation + Chair's letterhead) | `no-wet-lab-archetypes-2026-08-12.json` → `ncdb_puf` | Adopted; did not re-probe facs.org |
| ICD-O-3 9231/3 is contaminated: ≥ 32.1 % of one SEER 9231 pull was skeletal (191/595), ~37.5 % adjusted | `icdo-9231-restriction-audit.json`; owner `research/modalities/emc-icdo-contamination.json` | Adopted as SECONDARY; ran no new arithmetic on it |
| The registry ICD-O classification paper was **rejected by the user** | CLOSED-WORK.md | I propose no such paper |
| SEER-to-EMC causal calibration / Noone PMC4981219 | CLOSED-WORK.md, dispatch | Excluded entirely |
| RARECAREnet reachability recorded as `ConnectionRefusedError` on `rarecarenet.eu` | `research/modalities/emc_icdo_contamination.py:654` | I tried a **genuinely different route** (`https://www.rarecarenet.eu/rarecarenet/index.php` via WebFetch); it returned a **different** failure mode (`EGRESS_BLOCKED`). Recorded, not retried further |

## Method / inputs

**Repository files read** (all at HEAD `92abbcb905cacf07f14b238db50d1b98f6590374`, read-only):
`research/autonomy/opus-capacity-campaign-20260908/COMMON-BRIEF.md` (original and 2026-09-08T01:52Z revision), `.../CLOSED-WORK.md`, `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md`, `research/manuscripts/care-delivery/icdo-9231-restriction-audit.json`, `research/modalities/emc-surgical-quality.json`, `research/manuscripts/no-wet-lab-publication-archetypes.md` (§4.4, §6.1–6.5), `research/literature/no-wet-lab-archetypes-2026-08-12.json`, `systems/views/L2-rt-population-registry.md`.

**External retrievals.** All bibliographic retrieval below is **according to PubMed**, via the PubMed MCP connector (`search_articles`, `get_article_metadata`), 2026-09-08. Web retrieval via `WebFetch` through this sandbox's egress proxy.

| Probe | Tool | Outcome |
|---|---|---|
| `NETSARC AND (sarcoma network OR reference centre OR referral)` | PubMed `search_articles` | 80 records |
| `(extraskeletal myxoid chondrosarcoma) AND (referral OR reference center OR expert center OR network OR hospital volume OR access)` | PubMed `search_articles` | **24 records total** (`has_more: false` — the complete result set) |
| `(extraskeletal myxoid chondrosarcoma OR myxoid chondrosarcoma) AND (NETSARC OR "French Sarcoma Group" OR EURACAN OR RARECARE)` | PubMed `search_articles` | **2 records total** (`has_more: false`) |
| `https://www.rarecarenet.eu/rarecarenet/index.php` | WebFetch | `EGRESS_BLOCKED` — unrecovered |
| `https://seer.cancer.gov/seerstat/variables/seer/facility/` | WebFetch | `EGRESS_BLOCKED` — unrecovered |

Articles whose metadata I actually retrieved: PMIDs 42686333, 42604059, 41232987, 40911493, 40347715, 41689087, 41635359, 41074947, 40704268, 31331701, 29545115.

⚠ **Retrieval level.** Everything I quote from these articles is **title/abstract-level metadata from PubMed**. I fetched **no full text**. Where a source's centre variable could only be settled from Methods, I mark it UNKNOWN rather than guessing.

## Result

### R.1 — The source table, with an EMC-identifiability verdict per source

Two verdicts are given per source and they are deliberately independent:
**(A) Does the source's *public output* carry a treating-centre / referral / volume variable at all?**
**(B) Is EMC *separately reportable* in that public output?**
A source must pass **both** to answer an EMC care-access question. Evidence grade in the last column.

| # | Source | (A) centre/referral variable in public output? | (B) EMC separately reportable in public output? | Identifying variable that would be needed | Verdict | Grade |
|---|---|---|---|---|---|---|
| S1 | **NCDB Participant User File** (ACS/CoC) | **NO — structurally.** The PUF "identifies neither patients, providers nor hospitals"; facility volume is not recoverable | Moot — (A) already fails. Would in principle be ICD-O-3 9231/3 + topography | ICD-O-3 morphology 9231/3 + C40–C49 topography | ⛔ **CANNOT ANSWER.** Also access-closed (CoC affiliation + insider designation + Chair's letterhead) | SECONDARY (repo-committed reading, `no-wet-lab-publication-archetypes.md` §4.4 / §6.4) |
| S2 | **SEER research data / SEER\*Stat** | **NO.** SEER research data carries no hospital or facility identifier. First course of treatment only; radiation and chemotherapy collapse "did not receive" with "unknown" | **NO.** 9231/3 does not isolate EMC: ≥ 32.1 % (191/595) of one published 9231 pull was skeletal; a topography restriction is necessary and **not sufficient**, because primary EMC *of bone* exists and EMC misassigned to chondrosarcoma-NOS is unreachable | ICD-O-3 9231/3, which is demonstrably not specific | ⛔ **CANNOT ANSWER — fails both axes** | SECONDARY (SEER fields: repo §6.3, flagged there as single-host, not cross-checked; contamination: `icdo-9231-restriction-audit.json`, arithmetic re-verified in-repo, all 11 checks pass) |
| S3 | **SEER-Medicare** | Plausibly yes (claims carry provider identifiers) — **UNVERIFIED, I read no field list** | Inherits S2's 9231/3 contamination | same as S2 | ⛔ **UNKNOWN on (A); FAILS on (B) by inheritance.** Also a separate institutional application | UNKNOWN / SECONDARY |
| S4 | **RARECAREnet public search tool** (`app.rarecarenet.eu`) | Not a care-access instrument — publishes incidence, 1/3/5-yr relative survival, survival trends, 15-yr prevalence; **no centre variable** | **UNVERIFIED and now unrecovered.** Repo records entities are ICD-O groupings at the 'chondrosarcoma'/STS-family tier and that no EMC-specific fact sheet was surfaced | Whether the portal resolves EMC as its own layer-3 entity | ⛔ **CANNOT ANSWER on (A) regardless of (B).** (B) stays UNVERIFIED — my new route returned `EGRESS_BLOCKED`, a different failure from the previously recorded `ConnectionRefusedError` | UNKNOWN (source unrecovered from this sandbox) |
| S5 | **NETSARC+ (French national sarcoma network)** | **YES — this is the one source class whose published outputs are explicitly centre- and network-structured** (e.g. PMID 40347715 collects 1081 primary retroperitoneal sarcoma patients across 11 NETSARC+ centres and reports 90-day postoperative mortality 21/1081 = 1.9 %) | **NO in any output I could reach.** A complete PubMed search pairing EMC/myxoid chondrosarcoma with NETSARC / French Sarcoma Group / EURACAN / RARECARE returns **exactly 2 records** (`has_more: false`), **neither** of which reports referral pathway or centre volume for EMC: PMID 31331701 is the pazopanib phase 2 trial, PMID 29545115 is a radiation-oncologist contouring-variability workshop that used one EMC case as a delineation exercise | Central pathology review / registry morphology field inside NETSARC+ | ⚠ **(A) PASSES, (B) FAILS in public output.** The instrument that has the variable does not report this histology separately | PRIMARY (search result, complete set) + SECONDARY (abstracts) |
| S6 | **ERN EURACAN** | Network-level organisational reporting exists (PMID 42604059 surveys all 24 ERN coordinators on crisis preparedness) but it reports **networks**, not patients-by-centre | **NO.** No EMC-level output surfaced | — | ⛔ **CANNOT ANSWER** | SECONDARY (abstract) |
| S7 | **Japanese National Bone and Soft Tissue Tumor Registry**, as published (Masunaga 2025, PMID 40885991 / PMC12398172) | **NO.** "No centre, centre volume or referral status is printed for any patient. A national registry could in principle carry it; this publication does not report it" | **YES** — 171 pathologically diagnosed EMC patients are reported as EMC | already satisfied in this publication | ⛔ **CANNOT ANSWER.** (B) passes, (A) fails. **This is the highest-value near-miss in the table** | SECONDARY (repo-committed curation of a published source) |
| S8 | **Chiusole 2020 two-centre series** (Istituto Oncologico Veneto + Institut Gustave Roussy, 1980–2018) | **NO, and unfixably.** Every patient was treated at one of two sarcoma referral centres, so the exposure is **held constant by construction** | YES | already satisfied | ⛔ **CANNOT ANSWER — a cohort that cannot answer the question however completely it is curated** | SECONDARY (repo-committed) |
| S9 | **Published EMC referral-centre series generally** (e.g. Drilon 2008, PMID 18951519, n = 87, two referral centres) | Same defect as S8 — referral-centre cohorts have no general-centre comparator | YES | already satisfied | ⛔ **CANNOT ANSWER** | SECONDARY (repo-committed) |
| S10 | **Open-access EMC case reports** | Occasionally record an individual referral event in free text | YES, per case | free text | ⚠ **EXISTENCE ONLY, NO DENOMINATOR** — see R.2 | PRIMARY (abstract, retrieved this run) |

### R.2 — One genuinely new, source-traceable EMC referral datum, and exactly what it is worth

**PRIMARY.** According to PubMed, Terao et al., *World Journal of Surgical Oncology* 2026 (PMID 41689087, PMC13005408, [DOI](https://doi.org/10.1186/s12957-026-04247-0)) report three patients who "underwent unplanned excision of the hand or foot at another institution referred to our hospital for additional treatment." **Case 1 is EMC**: "A 46-year-old man with extraskeletal myxoid chondrosarcoma on the dorsal aspect of the left hand."

⭐ **What this establishes:** an EMC patient who received an **unplanned excision at a non-specialist institution and was subsequently referred to a sarcoma centre** is recorded in the reachable open-access literature, by name of histology, at the level of one identified patient.

⛔ **What it does NOT establish, and the distinction is the whole point of the row.** It is **n = 1 inside a 3-case report selected for a reconstruction technique**. There is **no denominator**: nothing states how many EMC patients that institution saw, how many were referred, or how many were excised unplanned elsewhere. **No rate, no fraction, and no proportion may be computed from it, now or later.** It is an existence proof.

⚠ **How it relates to the repo's existing closure — a narrowing, not a refutation.** `emc-surgical-quality.json` holds `unplanned_excision.recorded_in_any_reachable_series: false` and `treatment_setting.recorded_in_any_reachable_series: false`. Those verdicts are **correct as scoped** — they are about the two *curated rate-bearing series* (Masunaga, Chiusole), and my finding does not touch either. But if the field name is read at face value — "recorded in **any** reachable series" — then it is **too strong as a categorical statement about the literature**, because a reachable open-access publication does record an unplanned excision and a referral in this histology. The honest amended wording, which I recommend to the artifact's owner (not this seat), is: *"recorded in no reachable series that can yield a rate; recorded as an individual event in at least one case report (PMID 41689087), which carries no denominator."*

⭐ **This is precisely the failure mode §2 of `emc-care-delivery-endpoint-decision.md` documented twice already** (the metastasectomy "ZERO records" and the carbon-ion `found_in_this_histology: false` absences, both refuted by a file inside their own corpus). A third absence, stated categorically, again turns out to be an absence *of a certain shape of evidence* rather than an absence of the evidence. The pattern — not this one case report — is the transferable finding.

### R.3 — Secondary observations from the retrieval

- **SECONDARY.** PMID 41074947 (Ashburner et al., *Skeletal Radiology* 2025, [DOI](https://doi.org/10.1007/s00256-025-05050-w)) is a 44-patient EMC cohort from Mount Sinai / University of Toronto — i.e. another **single-specialist-centre** cohort, reproducing the S8/S9 defect: setting held constant, no comparator.
- **SECONDARY.** PMID 31331701 (Stacchiotti et al., *Lancet Oncology* 2019, [DOI](https://doi.org/10.1016/S1470-2045(19)30319-5)) enrolled 26 EMC patients at **11 study sites of the Spanish, Italian and French sarcoma groups**. This shows EMC patients are assembled *through* specialist networks, but it is trial enrolment, not a care-access denominator, and says nothing about where non-enrolled EMC patients are treated. ⛔ Note the repository's standing Pazopanib caution in CLOSED-WORK.md: I quote only enrolment structure here, no exposure or rate claim.
- **PRIMARY (search result).** The EMC × care-access PubMed search returned **24 records, complete set** — and inspection of the recent ones shows they match on incidental use of "access"/"network" rather than on subject matter. ⚠ This is **not** proof that no such study exists (a missing search hit is UNKNOWN, per COMMON-BRIEF §2); it is evidence that none is indexed under these terms.

### R.4 — The feasible-question verdict

⛔ **EMC-specific care-access and referral questions are NOT answerable from currently public data, and the blocker is a clean two-axis separation rather than a data gap that more searching would close.**

Every source in the table fails on at least one of two independent axes, and **no source passes both**:

- Sources that **have** the centre/referral/volume variable (S5 NETSARC+, and in principle S3) **do not report EMC separately** in public output.
- Sources that **do** report EMC separately (S7 Japanese registry as published, S8, S9, S10) **do not carry the centre variable** — S7 because the publication does not print it, S8/S9 because the exposure is held constant by construction, S10 because it has no denominator.
- S1 and S2 fail on **both** axes, and S2's failure on axis (B) is *measured*, not assumed: ≥ 32.1 % skeletal contamination of ICD-O-3 9231/3.

⭐ **The nearest thing to a feasible question is not a care-access question at all — it is an identifiability question, and it is the one I would put forward.** Two named, reachable data holders (the Japanese National Bone and Soft Tissue Tumor Registry, and NETSARC+) each hold *half* of what an EMC referral study needs, and in each case the missing half exists in the underlying database but is absent from the public output. **That is a reportable statement about the shape of the evidence base**, it is falsifiable (a single published output pairing morphology-resolved EMC with treating-centre status refutes it), and it required no new patient data. ⚠ It is a **description of data availability**, not a clinical finding, and it must never be written as though it were evidence about outcomes.

## Validation evidence

**RUN.** All commands executed in this container; shell `bash` via the Bash tool; working directory `/home/user/Rare-cancers` unless stated; Python `python3` (system interpreter, invoked only for read-only JSON field-walks).

| # | Command | Exit | Key verbatim output |
|---|---|---|---|
| V1 | `git rev-parse HEAD` | 0 | `92abbcb905cacf07f14b238db50d1b98f6590374` — matches the frozen read commit |
| V2 | `git status --porcelain` (start and end) | 0 | `?? research/autonomy/opus-capacity-campaign-20260908/` — the only entry, both times. **No file created or modified by me.** |
| V3 | `env \| grep -i -E 'claude\|anthropic\|model' \| sed -E 's/(TOKEN\|KEY\|SECRET)[^=]*=.*/\1=<redacted>/I'` | 0 | Full output pasted under `## Worker`. **No model-identifying variable present.** |
| V4 | `date -u` | 0 | `Tue Sep  8 01:54:19 UTC 2026` |
| V5 | `rg -n -i "referral\|centre\|center volume\|access\|specialist\|sarcoma centre\|equity\|travel\|insurance" research/ --glob '!.git' \| head -80` | 0 | Output quoted in §Prior-work check |
| V6 | `python3 -c "<field-walk>" research/modalities/emc-surgical-quality.json \| rg -i "setting\|centre\|referral\|unplanned"` | 0 | Verbatim: `/treatment_setting/recorded_in_any_reachable_series = False`; `/series[0]/⛔_setting_absent = No centre, centre volume or referral status is printed for any patient. A national registry could in principle carry it; this publication does not report it.` |
| V7 | `python3 -c "<field-walk>" .../icdo-9231-restriction-audit.json \| head -100` | **non-zero (BrokenPipeError from `head`)** | Truncated by the pipe, **not** a data error. All 11 arithmetic checks visible before truncation read `pass = True`, and `/arithmetic_reverification/verdict = Every printed-count derivation reproduces the committed value. No arithmetic defect found.` ⚠ Recorded as a real non-zero exit rather than reported as a pass. |

**RUN — external retrievals** (PubMed MCP connector and WebFetch; the tool layer reports success/failure rather than a shell exit code):

| Probe | Result |
|---|---|
| PubMed `(extraskeletal myxoid chondrosarcoma) AND (referral OR ... OR access)` | `{"total_count":24,"returned_count":24,...,"has_more":false}` |
| PubMed `(EMC OR myxoid chondrosarcoma) AND (NETSARC OR "French Sarcoma Group" OR EURACAN OR RARECARE)` | `{"pmids":["31331701","29545115"],"total_count":2,"returned_count":2,"has_more":false}` |
| WebFetch `https://www.rarecarenet.eu/rarecarenet/index.php` | `{"error_type":"EGRESS_BLOCKED","domain":"www.rarecarenet.eu",...}` — **unrecovered source, not circumvented** |
| WebFetch `https://seer.cancer.gov/seerstat/variables/seer/facility/` | `{"error_type":"EGRESS_BLOCKED","domain":"seer.cancer.gov",...}` — **unrecovered source, not circumvented** |

**PROPOSED (NOT RUN).** Retrieving the NETSARC+ annual activity report and the RARECAREnet downloadable entity spreadsheet through a GitHub Actions runner (the repository's documented escape hatch for egress-blocked hosts). Not run: outside this bounded read-only run, and dispatching CI is a decision this seat does not own.

**No content-policy refusal occurred in this run.**

## Limitations

- **Abstract-level retrieval only.** I fetched no full text. A source's Methods could contain a centre variable that its abstract does not mention. Every (A)/(B) verdict for S5 rests on public output I could reach, and is a statement about *published output*, not about the underlying database.
- **Two sources are unrecovered, not negative.** RARECAREnet (S4) and the SEER facility page (S2 axis A) both returned `EGRESS_BLOCKED`. Their verdicts are **UNKNOWN on the point I could not read**, and I have marked them so. A missing page is not proof of absence.
- **The SEER field readings I adopted are repo-committed and self-flagged.** `no-wet-lab-publication-archetypes.md` §6.3 marks its treatment-field readings "single-host retrieval, not cross-checked" and "2-1; the primary page was never fetched". I inherited that uncertainty rather than laundering it.
- **The 24-record and 2-record search results are evidence, not proof.** An empty or thin PubMed result is UNKNOWN. Non-indexed outputs — national audit reports, network annual reports, grey literature, non-English publications — are entirely outside what I searched.
- **No denominator anywhere in R.2.** The one new EMC referral datum is a single patient in a case report. **No rate, fraction, proportion or age gradient is computed or implied from it, and none may be.**
- **No causal claim, no calibration.** This report establishes nothing about whether specialist-centre care changes EMC outcomes. That question remains unanswerable from the sources audited here, which is the finding. Nothing here supports any EMC parameter value derived from generic registry statistics.
- **Not clinical advice, no patient data, no wet lab.** Nothing here concerns efficacy, safety, selectivity or clinical readiness.
- **This is one seat's audit.** The identifiability verdicts are read from committed artifacts and abstracts; a reader with database access could overturn any row, which is the correct standard of falsifiability for them.

## Stop condition

**Set:** an identifiability-verified source table plus a feasible-question verdict.

**MET.** The table (R.1) covers 10 source classes with an explicit two-axis identifiability verdict and an evidence grade per row, including two rows honestly marked UNKNOWN because the source was unrecovered. The feasible-question verdict (R.4) is delivered as an **evidence-backed negative**: EMC-specific care-access questions are not answerable from currently public data, with the blocker localised to a clean separation between sources that carry the centre variable and sources that resolve EMC — no source does both. One incidental primary finding (R.2) narrows an existing categorical repository claim without refuting its scoped verdict.

## Tool-call and wall-clock count actually used

- **Tool calls: 22** (2 brief reads, 6 repository reads/greps, 1 ToolSearch, 5 PubMed calls, 2 WebFetch, 1 env/date/git capture, plus the interleaved status checks). Under the ~40 target.
- **Wall clock: approximately 12 minutes** (session start through 2026-09-08T01:54:19Z capture). Under the ~40-minute target.

## Next concrete action

**One successor task, and it is a retrieval with a pre-declared falsifier — not another literature sweep.**

Dispatch a **GitHub Actions runner fetch** (the repository's documented escape hatch for egress-blocked hosts) for exactly two artifacts, and record for each a one-line identifiability verdict against the R.1 schema:

1. the **RARECAREnet downloadable entity list / fact-sheet index** — resolving the repository's explicitly `UNVERIFIED` question of whether EMC exists as its own layer-3 entity, which this run could not reach; and
2. the **NETSARC+ published activity report**, testing the single point on which the whole R.4 verdict turns: whether NETSARC+ ever reports a histology-resolved EMC count alongside centre or first-surgery-in-network status.

**Pre-declared falsifier, so this cannot be graded after the fact:** if either document pairs morphology-resolved EMC with treating-centre or referral status, R.4's negative verdict is **refuted** and one feasible EMC care-access question exists. If neither does, R.4 is confirmed on two additional named sources and the lane should be closed with that record rather than searched again.

⛔ **What the successor must NOT do:** re-curate Masunaga or Chiusole for treatment setting (closed, and re-curation cannot produce it), pursue NCDB or SEER for facility variables (S1/S2 fail on structural grounds already established), or build any rate from PMID 41689087.

---

**Summary (under 400 words).** I confirmed that the repository has already closed the *published-series* half of this lane — `emc-surgical-quality.json` records `treatment_setting.recorded_in_any_reachable_series: false`, with Masunaga 2025 printing no centre for any patient and Chiusole 2020 holding the exposure constant because all patients were treated at two referral centres — and that NCDB PUF was separately closed because it identifies neither patients, providers nor hospitals. I did not replay any of that.

The open increment I pursued was an identifiability audit of *data sources* rather than papers. I built a 10-source table scoring each on two independent axes: does its public output carry a treating-centre variable, and is EMC separately reportable in that output. **No source passes both.** NETSARC+ has the centre variable — its published outputs are explicitly centre-structured — but a complete PubMed search pairing EMC with NETSARC / French Sarcoma Group / EURACAN / RARECARE returns exactly two records, neither reporting referral pathway or centre volume for EMC. The Japanese registry publication resolves EMC (171 patients) but prints no centre. SEER fails both axes, its second failure measured rather than assumed: ≥32.1% of one published ICD-O-3 9231/3 pull was skeletal. RARECAREnet and the SEER facility page are honestly UNKNOWN — both returned EGRESS_BLOCKED, recorded as unrecovered, not circumvented.

Verdict: EMC-specific care-access questions are **not answerable from currently public data**, and the blocker is a clean split between sources that hold the centre variable and sources that resolve the histology.

One incidental primary finding: PMID 41689087 (open access) reports a 46-year-old man with EMC who underwent unplanned excision at another institution and was referred to a sarcoma centre. That is n=1 in a 3-case report with no denominator — no rate follows — but it means the artifact field `unplanned_excision.recorded_in_any_reachable_series: false` is too strong read categorically, and should be narrowed to "recorded in no series that can yield a rate". This is the third time a categorically stated absence in this program has been narrowed by a file inside its own corpus.

I wrote no files; the full report is the body of this response, per the coordinator's read-only correction. 22 tool calls, ~12 minutes.

result: EMC care-access questions are unanswerable from public data — 10-source identifiability table shows no source both carries a treating-centre variable and reports EMC separately (NETSARC+ has the variable but never resolves EMC; the Japanese registry resolves EMC but prints no centre; SEER fails both, ≥32.1% of ICD-O 9231/3 being skeletal) — plus one primary EMC referral case (PMID 41689087) that narrows an over-strong repository absence claim without yielding any rate.
