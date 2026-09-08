<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:10:00Z UTC
     agent id aaba2d2ae64382a85 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aaba2d2ae64382a85.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Recording complete. Report follows.

---

## Worker

- **Worker:** W09f, lane 9 refill, OPUS-CAPACITY-CAMPAIGN-20260908.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No `env` variable names a model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the served model from the transcript.
- **Write isolation honoured.** Nothing was written into `/home/user/Rare-cancers`. No git write operation. All execution under `/tmp/claude-0/w09f/` on a `tar --exclude=./.git` scratch copy. `scripts/preflight.sh` not run.

`date -u` at start: `Tue Sep  8 02:58:15 UTC 2026`. At end: `Tue Sep  8 03:03:08 UTC 2026`.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0), model-relevant lines verbatim; the long `no_proxy` / `NO_PROXY` / `npm_config_noproxy` / `GLOBAL_AGENT_NO_PROXY` / `JAVA_TOOL_OPTIONS` proxy lines are elided as marked and nothing else was removed:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=…  [elided, proxy list]
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
GLOBAL_AGENT_NO_PROXY=…  [elided, proxy list]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=…  [elided, proxy/truststore]
NO_PROXY=…  [elided, proxy list]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=…  [elided, proxy list]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

⚠ **The tree moved under me and I report it rather than hide it.** `git rev-parse HEAD` was `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8` at 02:58:15Z and `a87275c14897230041fde97c9965c9646474df7a` at 03:03:08Z — the coordinator collecting other workers' reports (`W04d`, `W08h`, `W13f`, `W17h`). Neither commit touches `systems/graph/publications.json` or any file this report analyses: `diff -rq /home/user/Rare-cancers /tmp/claude-0/w09f/copy --exclude=.git` at the end lists **only** those four new report files, so the scratch copy's `publications.json` and all 107 committed view files are still byte-identical to the live tree.

⚠ Also note the campaign brief names the frozen read commit as `92abbcb…`; the checkout is well past it. Every reading below is at the HEADs quoted, not at `92abbcb`.

`git status --porcelain` at start: **empty**. At end: **empty**.

---

## Question

**Of the `why_not_written` and `what_it_would_claim` fields in `systems/graph/publications.json` that W09b/W09c/W09d/W09e never examined, how many assert a categorical absence, and how many of those are false or over-scoped against committed evidence — measured by sentinel substitution and regeneration, not by grep?**

Open because W09b's sweep covered `systems/graph/artifacts.json` notes and JSON *boolean* absence fields, W09c/W09d covered `artifacts.json` and `routes.json`, W09e covered exactly one field of `publications.json`, and the S18 sprint explicitly did not touch `systems/graph/*.json`. The prose fields of `publications.json` are a population nobody had counted.

---

## Prior-work check

Read in full first, as dispatched: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `systems/POLICY-evidence.md`, and `reports/W09b-absence-claim-audit.md`, `W09c-artifacts-contradiction-package.md`, `W09d-views-regeneration-proof.md`, `W09e-views-blast-radius.md` (the dispatch's `reports/` path is wrong — they live at `research/autonomy/opus-capacity-campaign-20260908/reports/`).

Commands run:

```
find . -path ./.git -prune -o -name 'W09*' -print
grep -n '"why_not_written"\|"what_it_would_claim"\|"id": "PUB' systems/graph/publications.json
grep -rn "RETRACT" research/modalities/nr4a3-fusion-targets.json
grep -rn "no targeted agent\|no approved targeted" --include=*.json --include=*.md --include=*.py .
grep -rn "pazopanib\|sunitinib" --include=*.json systems/graph/ research/data/emc-clinical-registry.json
grep -rn "occupancy alone\|monovalent" systems/graph/routes.json
grep -rn "clinical use addresses the driver" --include=*.json --include=*.md .
```

Not replayed: W09e's C5 correction and its wording decision (I reproduce its blast-radius number **as a control on my own method** and otherwise leave it alone); S18 items 2, 5, 6; the metastasectomy/carbon-ion corrections; `emc-perfusion-myxoid-search-2026-08-27.json` (no egress); PUB-EMC-CLASSIFICATION as a paper (user-rejected, closed — I audit only the *wording of its graph record*, not the route); the NR4A Perspective refusal; lane 11's source-index; every denied external route. **No network was used at all.**

⚠ **One correction to the dispatch's own arithmetic.** It says "the other 32 `why_not_written` / `what_it_would_claim` fields". The file holds **33 records carrying 41 such fields** — 33 `what_it_would_claim` and 8 `why_not_written`. Forty, not thirty-two, had never been audited.

---

## Method / inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `ce743d6a` → `a87275c1` | tree under test, read-only |
| `systems/graph/publications.json` (583 lines, 33 records) | the source under test |
| `systems/systems_check.py` | the generator actually run |
| `systems/views/` (**107 committed files**) | the generated layer |
| `research/modalities/emc-site-curation.json` | counter-evidence for PUB-LOCOREGIONAL |
| `research/modalities/nr4a3_fusion_targets.py:1904-1934` | the RETRACTION and `⛔_how_to_state_it` rule |
| `systems/graph/routes.json:3693, :6584, :7894, :8109` | counter-evidence for PUB-ANDGATE, PUB-KINASE-LEADS |
| `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md:424,587` | the committed correct restatement of "no targeted agent" |
| `research/manuscripts/care-delivery/emc-icdo-9231-classification.md:33` | counter-evidence for PUB-EMC-CLASSIFICATION |
| `/tmp/claude-0/w09f/copy/` | scratch copy; the only place anything was executed or modified |

Python 3.11 stdlib only. No network, no paid API, no GPU, no clinical claim.

Enumeration method: parse all 33 records; split every in-scope field into sentences; match a 40-term absence regex; then **hand-classify** each hit, because the regex over-fires massively on disclaimers ("asserts no efficacy"), self-scoped statements ("nothing here has been synthesised") and ordinary measurements. The defensible target class is W09b's: *a clause asserting, about a body of evidence (literature, corpus, cohorts, "anyone", "the field"), that some thing is not recorded, found, reported or studied there.*

---

## Result

### R.1 — The population, honestly narrowed `PRIMARY`

| pass | n |
|---|---|
| records in `publications.json` | **33** |
| in-scope fields (`what_it_would_claim` + `why_not_written`) | **41** (33 + 8) |
| fields containing ≥1 absence-shaped sentence (regex) | **34** |
| fields carrying ≥1 **categorical** negative *about a body of evidence* | **17** |
| such **clauses** (some fields carry several) | **22** |

⭐ The regex-to-answer ratio is the same lesson W09b reported: 34 fields fire, 17 survive reading. Most of what fires is a *disclaimer* ("It asserts no efficacy, safety or clinical readiness for any agent" — PUB-ENDPOINT, PUB-FUSION-PARTNER, PUB-VACCINE-PATH) or a *self-scoped* statement about this programme's own work. Neither is this defect class, and counting them as absence claims would be the error this task exists to prevent.

### R.2 — All 22 categorical clauses, classified `PRIMARY`

| # | record · field · `file:line` | clause, quoted | verdict |
|---|---|---|---|
| 1 | `PUB-CARE-DELIVERY.why_not_written` · `publications.json:119` | *"treatment setting is reported by no reachable series"* | ⛔ **FALSE** — known, W09e. Not re-litigated. |
| 2 | `PUB-LOCOREGIONAL.why_not_written` · `:305` | *"no cohort carries a primary anatomical site field"* | ⛔ **FALSE** — see R.3 |
| 3 | `PUB-LOCOREGIONAL.why_not_written` · `:305` | *"metastatic site appears once in free text rather than as data"* | ⛔ **FALSE** — see R.3 |
| 4 | `PUB-KINASE-LEADS.what_it_would_claim` · `:286` | *"none has been followed up by anyone"* | ⛔ **FALSE** — see R.4 |
| 5 | `PUB-LOCOREGIONAL.why_not_written` · `:305` | *"no cohort records … time-to-metastasis"* | ⚠ **OVER-SCOPED** — R.3 |
| 6 | `PUB-KINASE-LEADS.what_it_would_claim` · `:286` | *"in a disease with no targeted agent"* | ⚠ **OVER-SCOPED** — R.4 |
| 7 | `PUB-FUSION-OUTPUT.what_it_would_claim` · `:223` | *"No experiment has measured where an NR4A3 fusion binds, or what chromatin does, in EMC material"* | ⚠ **OVER-SCOPED** — R.5 |
| 8 | `PUB-EMC-CLASSIFICATION.what_it_would_claim` · `:168` | *"the resulting contamination is MEASURED here for the first time"* | ⚠ **OVER-SCOPED** — R.6 |
| 9 | `PUB-ANDGATE.what_it_would_claim` · `:11` | *"it names precisely what does not exist for it to be built, which is a ligand for the EWSR1 half"* | ⚠ **OVER-SCOPED** — R.7 |
| 10 | `PUB-PARKED-MODALITIES.why_not_written` · `:438` | *"Every route it would cover is parked on a technology nobody has"* | ⚠ **OVER-SCOPED** — R.8 |
| 11 | `PUB-MONOVALENT.what_it_would_claim` · `:370` | *"the question of whether occupancy alone changes the fusion's behaviour has never been asked by anyone"* | ❓ **UNVERIFIABLE** — R.9 |
| 12 | `PUB-METHODS.what_it_would_claim` · `:337` | *"the field publishes almost none of them"* | ❓ **UNVERIFIABLE** — R.9 |
| 13 | `PUB-FUSION-PARTNER.what_it_would_claim` · `:239` | *"a magnitude this contrast has never had"* | ❓ **UNVERIFIABLE** — R.9 |
| 14 | `PUB-NR-OUTSIDE-NR4A3.why_not_written` · `:421` | *"reported in one EMC patient in the world literature"* | ❓ **UNVERIFIABLE** — R.9 |
| 15 | `PUB-EMC-PROGRAM.what_it_would_claim` · `:191` | *"nothing in clinical use addresses the driver"* | ✅ **TRUE** — this is the correctly-scoped form; the peer-review-endorsed wording (R.4) says the same thing |
| 16 | `PUB-LOCOREGIONAL.why_not_written` · `:305` | *"no cohort records lesion burden"* | ✅ **TRUE** — `emc-site-curation.json` → `⛔_what_is_still_not_computable/lesion_burden`: *"no series prints per-patient lesion counts"* |
| 17 | `PUB-IPD-SURVIVAL.what_it_would_claim` · `:269` | *"the two largest print seven Kaplan-Meier curves between them and NO numbers-at-risk row"* | ✅ **TRUE** — measured twice by two methods, `routes.json:8109` (`km_risk_row_detect.py`, both readings agree on all nine figures) |
| 18 | `PUB-NEOANTIGEN.what_it_would_claim` · `:404` | *"NO proteome-wide search has ever been run"* | ✅ **TRUE** — self-scoped to this repository in its own sentence (*"the only novelty test in this repo … `fusion_breakpoints.py:231`"*) and self-flagged as a limit on the claim |
| 19 | `PUB-TCIP.what_it_would_claim` · `:523` | *"'ADMITS' is an excluded-volume statement no tested body has ever failed"* | ✅ **TRUE** — scoped to bodies actually tested |
| 20 | `PUB-MODALITY-CENSUS.what_it_would_claim` · `:352` | *"the classes nobody had pointed at"* | ✅ **TRUE** — scoped by the census that defines the set |
| 21 | `PUB-BIOMARKER-DEP.what_it_would_claim` · `:101` | *"Four selecting features are absent"* | ✅ **TRUE** — scoped in the same sentence to *"expression data already public for this disease"* |
| 22 | `PUB-NR-OUTSIDE-NR4A3.what_it_would_claim` · `:419` | *"a receptor that has the published tool compound this program's own receptor never had"* | ✅ **TRUE** `SECONDARY` — attested repo-wide; I did not run an independent chemical-probe search this run |

**Tally: 4 FALSE (3 new), 6 OVER-SCOPED, 4 UNVERIFIABLE, 8 TRUE.** Of the 40 fields nobody had audited, **8 carry a defective clause** and **8 more carry a categorical clause that survives the check**.

⭐ **The base rate is worse in `publications.json` than W09b measured in the boolean JSON fields, and the reason is structural.** W09b found the JSON *field* layer largely correct because a per-row object's row *is* its scope. `publications.json`'s prose fields have no row to be scoped by, so a writer must supply the scope in words — and in 8 of 17 cases nobody did.

### R.3 — PUB-LOCOREGIONAL: two FALSE clauses, refuted by a curation artifact committed *after* the field was written `PRIMARY`

`systems/graph/publications.json:305` states:

> ⛔ But the ELIGIBILITY criteria are not extractable, because they were never curated: **no cohort carries a primary anatomical site field, metastatic site appears once in free text rather than as data**, and no cohort records lesion burden or time-to-metastasis.

The committed counter-record is `research/modalities/emc-site-curation.json`, generated by `research/modalities/emc_site_curation.py`, whose own header says why it exists:

> `/_what` = *"Anatomical site of the primary tumour and of the metastases in extraskeletal myxoid chondrosarcoma, transcribed from the primary reports of the open-access series."*
>
> `/_why` = *"emc-locoregional-eligibility.json records primary site as NOT computable and metastatic site as computable only from one free-text note, and names re-curation from the primary reports as the highest-value step the locore…"*

It carries **three series with per-site integer counts** — chiusole2020 n=59, masunaga2025 n=171, bishop2019 n=41 (**271 patients**), plus drilon2008 n=86 as percentage-only context:

> `/series/0/printed_in` = *"TABLE 1 | Patients' characteristics — 'Primary Location (n. 59)' and 'Metastatic Sites (n. 26)'"*
> `/series/0/primary_site_counts/lower limb` = `40`, `upper limb` = `6`, `chest` = `3`, `abdomen` = `7`, `other` = `3`

**Clause 2 is FALSE**: three cohorts carry a primary anatomical site field, transcribed as data. **Clause 3 is FALSE**: metastatic site is carried as data in `Metastatic Sites (n. 26)` and in a four-row `lung_confined_readings` block across three series, not "once in free text".

⛔ **The same file contradicts itself.** `PUB-CARE-DELIVERY.why_not_written` at `publications.json:119` — three lines earlier in the same JSON array — already cites *"271 patients' primary site (emc-site-curation.json)"* as an existing extraction artifact. One record of `publications.json` names the artifact that refutes another record of `publications.json`.

**Clause 4 splits.** `⛔_what_is_still_not_computable/lesion_burden` = *"no series prints per-patient lesion counts"* → the lesion-burden half is **TRUE**. `⛔_what_is_still_not_computable/time_to_metastasis` = *"printed as a median in one series (5.9 years, chiusole2020) and as a median time to distant metastasis in another (28 months, bishop2019), and nowhere per patient"* → "no cohort records time-to-metastasis" is **OVER-SCOPED**; two cohorts record it, as a median rather than per patient.

**Smallest correct restatement** (rule-1.2 retention form), backed entirely by `emc-site-curation.json`:

> ⚠ Superseded, retained (rule 1.2): "no cohort carries a primary anatomical site field, metastatic site appears once in free text rather than as data, and no cohort records lesion burden or time-to-metastasis." Re-curated on 2026-08-27: three series now carry primary site as integer counts over 271 patients and metastatic site as data (`research/modalities/emc-site-curation.json`). What remains uncomputable is narrower and is that file's own reading — **no series prints per-patient lesion counts**, and time-to-metastasis is printed as a median in two series and **nowhere per patient** — so an oligometastatic threshold fraction still cannot be stated.

### R.4 — PUB-KINASE-LEADS: one FALSE clause and one OVER-SCOPED clause `PRIMARY`

`publications.json:286`: *"…and **none has been followed up by anyone**, in a disease with **no targeted agent**."*

**"none has been followed up by anyone" is FALSE.** `systems/graph/routes.json:6584` records, verbatim:

> *"PMID 29937513 (Urbini et al., Int J Mol Sci 2018, PMC6073125, DOI 10.3390/ijms19071855) is by the SAME GROUP as the 2014 activation report — Stacchiotti, Casali, Pantaleo, Dei Tos, Maestro, Dagrada and Pilotti are all authors of both — and its abstract states, verbatim: 'Recently, we reported on the therapeutic activity of sunitinib in a series of EMC cases, however the molecular target of sunitinib in EMC is unknown.'"*

That is the originating group publishing a follow-up on the strongest of the four leads. The same field also records PMID 28423517 restating the RET observation in full text. A follow-up exists and this repository has read it.

**"in a disease with no targeted agent" is OVER-SCOPED, and the repository has already written the correct form.** `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md:424`:

> **m6.** *"The abstract's "for which no targeted agent exists" is stronger than reference [1] supports, which is "no clinically validated agent directly targets NR4A3". Align the two; the weaker form costs three words and is unassailable."*

and item 36 at `:587` repeats it as an actionable instruction. Independently, `routes.json:7894` quotes the field's most recent comprehensive review recommending *"favour pazopanib after anthracycline failure"* — pazopanib is an approved targeted agent given in this disease, so "no targeted agent" is false read categorically. `PUB-EMC-PROGRAM` at `:191` already says the defensible thing (*"nothing in clinical use addresses the driver"*).

**Smallest correct restatement:**

> …⚠ Superseded, retained (rule 1.2): "and none has been followed up by anyone, in a disease with no targeted agent." One lead **was** followed up — by the group that reported it, which then called the target unknown (PMID 29937513, `systems/graph/routes.json`) — and the disease does receive targeted agents; what it has is **no clinically validated agent directly targeting NR4A3** (the form `emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md` m6 requires). What is true of all four leads is that **none has been taken to a prospective EMC-specific test.**

⚠ The last sentence is the one clause I could not verify exhaustively this run; if the graph's owner will not accept it, the honest negative form is *"none has been followed up in any record this repository has retrieved"* — a bounded statement about a search, which is `nr4a3_fusion_targets.py`'s own rule (R.5).

### R.5 — PUB-FUSION-OUTPUT: OVER-SCOPED by the repository's own stated rule, **not false** `PRIMARY`

`publications.json:223`: *"No experiment has measured where an NR4A3 fusion binds, or what chromatin does, in EMC material…"*

⭐ This sentence is verbatim "the claim that replaces the retracted one" written into `research/modalities/nr4a3_fusion_targets.py:1917-1918`, so it is the *corrected* text and GSE243553 does **not** refute it (that screen is *"ACCESSIBILITY and not occupancy, HEK293T and not EMC"*). **It is not a C6-style live contradiction.**

But the same generator, 12 lines later, states the rule this wording breaks:

> `⛔_how_to_state_it`: *"'No EWSR1::NR4A3 cistrome has been retrieved in 2,276 documents across five committed corpora' — a bounded negative about a SEARCH. It is NOT 'no such dataset exists': this searched retrieved full text, not all of PubMed, and a dataset can be deposited without a paper. **AN ABSENT READING IS NOT A READING OF ABSENCE.**"*

"No experiment has measured…" is a statement about the world; what was measured is a search. The retraction itself is the demonstration that this exact inference failed once already, on the same route, four weeks ago.

**Smallest correct restatement:** *"No experiment measuring where an NR4A3 fusion binds, or what chromatin does, in EMC material has been retrieved — across 2,276 full-text documents in five committed corpora and a 2026-08-08 sweep of the primary sequence archives (`research/manuscripts/fusion-output/nr4a3-cistrome-search-2026-08-08.md`) — while the same archives hold chromatin maps for EWSR1::WT1, EWSR1::ATF1, EWSR1::FLI1, FUS::DDIT3 and, twice, HEY1::NCOA2."* Every element is committed; only the scope word changes.

### R.6 — PUB-EMC-CLASSIFICATION: OVER-SCOPED against its own document `PRIMARY`

`publications.json:168` asserts *"the resulting contamination is **MEASURED here for the first time**."* Its own `document`, `research/manuscripts/care-delivery/emc-icdo-9231-classification.md:33`, says:

> *"measurement in section 6 is real and, **as far as a bounded search could tell, unpublished**."*

The note is scoped; the graph record is not. **Smallest correct restatement:** *"…and the resulting contamination is measured here — unpublished as far as a bounded search could tell (`research/manuscripts/care-delivery/emc-icdo-9231-classification.md`)."* ⚠ This route is user-closed as a paper; the fix is to the *record*, and does not reopen it.

### R.7 — PUB-ANDGATE: OVER-SCOPED against its own route `PRIMARY`

`publications.json:11` asserts the design *"names precisely what does not exist for it to be built, which is a ligand for the EWSR1 half."* `systems/graph/routes.json:3693` holds the same subject as an **open question**:

> *"Whether any ligand exists for the EWSR1 half — the second arm's chemistry does not exist."*

The graph's route layer says UNKNOWN; the publication layer says DOES NOT EXIST. **Smallest correct restatement:** *"…and it names precisely what the design lacks: **no ligand for the EWSR1 half has been retrieved, and whether any exists is open** (`systems/graph/routes.json` → `RT-ANDGATE` open questions)."* ⚠ The identical sentence also sits in `PUB-ANDGATE.outcome_potential_why` at `publications.json:16`, a field **outside my dispatched scope** — flagging it so the lander fixes both or neither.

### R.8 — PUB-PARKED-MODALITIES: OVER-SCOPED `PRIMARY`

`publications.json:438`: *"Every route it would cover is parked on **a technology nobody has**…"* Its own `what_it_would_claim` at `:437` names the three watched capabilities *"a glue design method with a prospective track record, a co-folder benchmarked on assembly, a solid-tumour vector"* — i.e. the claim the record actually supports is that **this programme cannot reach them**, converted to *"a monitored condition"*. "Nobody has" is a claim about the state of the world's technology with no committed census behind it.

**Smallest correct restatement:** *"Every route it would cover is parked on a capability this programme cannot reach, and each park carries a named scan trigger for the capability's arrival, so the paper has no result to report and would be a horizon scan."* ⚠ The same over-scoping appears in this record's `working_title` — *"Five modalities parked on a capability that does not exist yet"* — again **outside my dispatched field scope**, flagged not fixed.

### R.9 — The four UNVERIFIABLE clauses, and what would settle each `PRIMARY`

| clause | what would settle it |
|---|---|
| `PUB-MONOVALENT:370` *"has never been asked by anyone"* | A committed, bounded search record for the occupancy question, in the shape `nr4a3-fusion-targets.json` uses (named corpora, document count, date). `research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md:135` records a search only for a *different* paper (returning Zaienne 2022). Absent that, the honest form is *"no report asking it has been retrieved"*. |
| `PUB-METHODS:337` *"the field publishes almost none of them"* | A denominator: a count of methods papers screened and the fraction disclosing failed selectivity claims. None is committed. |
| `PUB-FUSION-PARTNER:239` *"a magnitude this contrast has never had"* | A retrieval record showing no prior published partner-stratified disease-specific mortality contrast. Not committed. ⚠ The rest of that sentence's numbers (7/15, 6/58, CIs) are separately sourced and are not in question. |
| `PUB-NR-OUTSIDE-NR4A3:421` *"reported in one EMC patient in the world literature"* | The partner-genotype census behind it, with its corpus and date. Not retrieved this run — a bounded negative about a search would be defensible; *"the world literature"* is not. |

⛔ In none of these four does committed evidence support a positive wording. **The honest negative form — a bounded statement about a search, with its corpus named — is the correct replacement, and I am not manufacturing a claim to fill the slot.**

### R.10 — Measured blast radius, by sentinel substitution and regeneration `PRIMARY`

Whole-field sentinel, generator run, views diffed against the committed set. **Real exit code 0 on every run** (`systems_check: wrote 111 view(s) to systems/views/`; the committed tree holds 107 files — the generator's own count is 111, and the control diff below shows the written set is byte-identical to the committed one, so the two numbers are the generator's accounting and the file count, not a discrepancy I introduced).

| record · field | files touched | committed lines consumed | sentinel occurrences | exit |
|---|---|---|---|---|
| `PUB-ANDGATE.what_it_would_claim` | **2** — `L2-rt-andgate.md:100`, `L3-publications.md:96` | 2 | 2 | **0** |
| `PUB-EMC-CLASSIFICATION.what_it_would_claim` | **3** — `L2-rt-diagnostic-pathway.md:71`, `L2-rt-population-registry.md:87`, `L3-publications.md:188` | 3 | 3 | **0** |
| `PUB-FUSION-OUTPUT.what_it_would_claim` | **2** — `L2-rt-fusion-output.md:83`, `L3-publications.md:226` | 2 | 2 | **0** |
| `PUB-KINASE-LEADS.what_it_would_claim` | **5** — `L2-rt-alk-hit.md:103`, `L2-rt-dnapk.md:102`, `L2-rt-ret.md:101`, `L2-rt-sgk1.md:99`, `L3-publications.md:431` | 5 | 5 | **0** |
| `PUB-LOCOREGIONAL.why_not_written` | **5** — `L2-rt-limb-perfusion.md:91`, `L2-rt-lung-directed.md:90`, `L2-rt-mdt-lung.md:83`, `L2-rt-rt-intensify.md:93`, `L3-publications.md:66` **and** `:452` | 6 | 6 | **0** |
| `PUB-PARKED-MODALITIES.why_not_written` | **5** — `L2-rt-af3-interface.md:90`, `L2-rt-crispr-cas13.md:95`, `L2-rt-glue.md:107`, `L2-rt-ribozyme.md:98`, `L2-rt-riptac.md:111`, `L3-publications.md:71` **and** `:544` | 7 | 7 | **0** |
| *control* `PUB-CARE-DELIVERY.why_not_written` | **5** files, 16 committed lines, 6 occurrences | 16 | 6 | **0** |

⭐ **The control reproduces W09e exactly** — 5 files, 6 occurrences, 16 committed lines (11 prose + 5 blank separators, because that field alone contains a literal `\n\n`). My method therefore agrees with the one that produced the finding this task extends.

⭐ **The 150-character clip decides two of the six, and I measured the offsets rather than assuming:**

| field | offending clause offset | field length | table row `L3-publications.md` changes on a clause-level fix? |
|---|---|---|---|
| `PUB-LOCOREGIONAL.why_not_written` | **521** | 1214 | ⛔ **No** — clipped away. Row `:66` renders only *"⚠ ITS BLOCKER WAS HALF RIGHT, AND THE HALF IT GOT WRONG IS THE INTERESTING ONE. …"*. A clause-level correction touches **5 lines** (4 L2 + `:452`), not 6. |
| `PUB-PARKED-MODALITIES.why_not_written` | **40** | 253 | ✅ **Yes** — the clause is the first sentence and is inside the clip. A clause-level correction touches all **7** occurrences in 6 files. |
| `PUB-KINASE-LEADS.what_it_would_claim` | 294 | 367 | n/a — `what_it_would_claim` is not the table's `gap` column; it renders once per L2 and once in the L3 detail. **5 lines, no clipped path.** |

⚠ **A lengthening restatement will renumber downstream lines** in the affected views — unlike W09e's C5 fix, which was length-neutral. The lander should regenerate and re-diff rather than reuse these line numbers after editing.

### R.11 — The transferable finding `PRIMARY`

W09b concluded the defect had migrated to *the summary layer*. This audit sharpens that: within the summary layer, the defect concentrates in **prose fields with no row to scope them**, and its commonest cause is **staleness** — a curation artifact lands (`emc-site-curation.json`, 2026-08-27) and the `why_not_written` that motivated it is never updated, so the graph goes on stating a gap the repository itself closed twelve days earlier. Two of the three FALSE clauses are of exactly this kind, and one of them is contradicted by a *sibling record three lines away in the same file*.

⛔ **No clinical claim is made anywhere in this report.** Every figure quoted (271 patients' primary site, n=59/171/41/86, 26 metastatic-site records) is a count of what was *reported*, with no outcome, comparator, rate or recommendation. Nothing here asserts efficacy, safety, tolerability or appropriateness of any agent, operation or pathway. There is no wet lab.

---

## Validation evidence

Environment for every run: scratch copy at `/tmp/claude-0/w09f/copy/`, produced by `tar --exclude=./.git -cf - . | tar -xf - -C …` from `/home/user/Rare-cancers` (`TAR_EXIT=0`; `cmp` on `publications.json` → `PUBS_IDENTICAL`). Linux, Python 3.11 stdlib, no network.

### `RUN` — Control: regeneration with no edit is a no-op
```
$ cd /tmp/claude-0/w09f/copy && python3 systems/systems_check.py --write-views
systems_check: wrote 111 view(s) to systems/views/
GEN_EXIT=0
$ diff -rq /tmp/claude-0/w09f/views-committed /tmp/claude-0/w09f/copy/systems/views
CONTROL_DIFF_EXIT=0
$ ls /tmp/claude-0/w09f/views-committed | wc -l
107
```
Idempotent at this HEAD, so every later diff is attributable to the sentinel alone.

### `RUN` — Seven whole-field sentinels (`/tmp/claude-0/w09f/sentinel.py`)
Each iteration asserts the encoded field value occurs **exactly once** in the file before substitution, writes the sentinel, regenerates, walks all view files (including the `registers/` subdirectory), counts sentinel occurrences and unified-diff `+/-` lines, then restores the pristine file and regenerates again. `SCRIPT_EXIT=0`. Verbatim output is transcribed into the R.10 table; every `GEN_EXIT` was `0` and every `gen_stdout` was `systems_check: wrote 111 view(s) to systems/views/`.

### `RUN` — Clip-offset measurement
```
PUB-LOCOREGIONAL      why_not_written       offset 521 of len 1214
PUB-PARKED-MODALITIES why_not_written       offset  40 of len  253
PUB-KINASE-LEADS      what_it_would_claim   offset 294 of len  367
```
plus the rendered `L3-publications.md` rows `:66`, `:69`, `:71` inspected directly, confirming the `…` truncation.

### `RUN` — Isolation proof
```
$ git status --porcelain          (start)   -> empty
$ git status --porcelain          (end)     -> empty
$ diff -rq /home/user/Rare-cancers /tmp/claude-0/w09f/copy --exclude=.git
Only in …/reports: W04d-duration-set-stability.md
Only in …/reports: W08h-remaining-missing-value-calls.md
Only in …/reports: W13f-cross-file-gate-coverage.md
Only in …/reports: W17h-welch-coverage-census.md
```
No difference in `systems/graph/`, `systems/views/`, or anything else. The four extra files are the coordinator's concurrent collections.

### `PROPOSED (NOT RUN)`
- **Correction diffs for the six defective clauses.** Only the *sentinel* radius was measured; I did not apply my proposed restatements and re-diff, because R.10 shows the restatements change field length and the lander must regenerate anyway. **The correction radii in R.10's clip table are derived from measured offsets, not from an applied edit.**
- **Acceptance tests.** Shape only, per the dispatch's warning: each must assert the superseded sentence is **quoted-and-superseded** inside `⚠ Superseded, retained (rule 1.2): "…"`, never **absent** — a bare grep will fire on the retained quotation. Not written, not run.
- `scripts/preflight.sh` — forbidden by dispatch, and no edit exists to gate.
- Independent retrieval of PMID 29937513, PMID 28423517, or any partner-genotype census — **no network authorised**; every quotation above is from a committed file.
- Landing anything. Nothing was applied to the repository.

---

## Limitations

- **The FALSE/OVER-SCOPED classification is an evidence comparison, not a literature search.** "FALSE" here means *a committed counter-record exists in this tree*. It does not mean I searched the literature; a clause I marked TRUE could still be false against sources this repository has never retrieved. `PUB-NR-OUTSIDE-NR4A3:419` is graded `SECONDARY` for exactly this reason.
- **The 22-clause count depends on my reading of the class boundary.** A stricter reader who counts disclaimers would get a much larger number; a looser one who requires an explicit "nobody/never" token would get about 12. I have quoted every clause so the boundary can be re-drawn without re-running anything.
- **Only two field names were audited.** `outcome_potential_why`, `working_title` and `posted._evidence` carry the same prose shape and are **outside the dispatched scope**; I found at least two categorical clauses in them (R.7, R.8) and did not audit them systematically. That is a real, named gap.
- **`R.4`'s proposed final sentence** (*"none has been taken to a prospective EMC-specific test"*) is the one restatement clause I could not fully verify; the fallback negative form is given in-line.
- **Line numbers are at `ce743d6a`/`a87275c1`** and view line numbers will shift once a length-changing correction is regenerated.
- **No clinical, efficacy, safety, selectivity or readiness claim** is made or implied. There is no wet lab. `systems/POLICY-evidence.md`'s binding scope is the clinical registry and pooled proportions derived from published cohorts; `systems/graph/publications.json` is outside it, and nothing proposed here touches a registry datum, a pooled proportion or an interval.
- **Nothing was landed**, no view was hand-edited, no test was authored or relaxed, and the retired patient-facing site was not recreated.

---

## Stop condition

Set up front: *return the moment every `why_not_written` / `what_it_would_claim` field in `publications.json` has been enumerated and classified, every FALSE/OVER-SCOPED field has a regeneration-measured blast radius with a real exit code, and every one of those has a smallest correct restatement or an honest negative form.*

**MET.** 41 fields enumerated, 22 categorical clauses classified, 6 defective fields sentinel-measured at `GEN_EXIT=0`, the C5 control reproducing W09e exactly, and a restatement or a stated settling condition for all ten non-TRUE clauses.

---

## Tool-call and wall-clock count actually used

**26 tool calls. 4 minutes 53 seconds wall clock** (02:58:15Z → 03:03:08Z). Well inside the ~40-call / ~40-minute target; I stopped when the condition was met rather than padding.

---

## Next concrete action

**Audit the three remaining prose field names in `systems/graph/publications.json` — `outcome_potential_why`, `working_title`, `posted._evidence` — by the same method, and then the same field names across `systems/graph/routes.json`, `strategies.json`, `modalities.json` and `objects.json`.** This is concrete, bounded and known-productive: two categorical clauses already surfaced in those fields incidentally (`PUB-ANDGATE.outcome_potential_why:16` repeats R.7's clause verbatim; `PUB-PARKED-MODALITIES.working_title` repeats R.8's), and `working_title` renders **inside the L3 table row**, so it is read more often than the field it duplicates. A lander who fixes only `what_it_would_claim` will leave the identical false sentence visible one line away.
