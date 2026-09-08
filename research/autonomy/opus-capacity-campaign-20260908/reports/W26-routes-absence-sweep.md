<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:23:21Z UTC
     agent id ac64b7d4fc3aa04b0 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ac64b7d4fc3aa04b0.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Recording complete. Report follows.

---

## Worker

- **Worker:** W26, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: graph-file false-absence audit, extending W09b → W09f onto `systems/graph/routes.json`.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model — `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the actual runtime model from the transcript.
- **Write isolation honoured.** Nothing written, moved or deleted under `/home/user/Rare-cancers`. No git write operation of any kind. All execution under `/tmp/claude-0/w26/` (scratch copy) and `/tmp/claude-0/w26x/` (scripts). `scripts/preflight.sh` not run. No network, no retrieval, no paid API, no GPU, no human contact, no publication.

`date -u` — start `Tue Sep  8 03:13:18 UTC 2026`, end `Tue Sep  8 03:19:06 UTC 2026`.

`git rev-parse HEAD` — start `98a0833f1ede2cf9cef13790388260567a32e868`, end `84f02dae1809ae050e40254f06310ed849982527`.

⚠ **HEAD moved under me and I report it rather than hide it.** The final `diff -rq /home/user/Rare-cancers /tmp/claude-0/w26 --exclude=.git` (DIFF_EXIT=1) lists **only** new campaign report files and two new campaign directories (`SAFETY-EVENTS.md`, `executed-artifacts`, and reports W02g, W04f, W05g, W09g, W12f, W16e, W17i, W18b, W19h, W20h, W21c) — the coordinator collecting siblings. **Nothing I measured changed:** `cmp` on `systems/graph/routes.json` → `ROUTES_STILL_IDENTICAL`, and no difference is reported in `systems/graph/`, `systems/views/` (107 committed files) or `systems/systems_check.py`. Note W09g's report landed during my run; it is `publications.json` and I did not read or touch it.

`git status --porcelain` — start: **empty**. End: **empty**.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0), verbatim except the four long proxy lines, which are marked elided and nothing else removed:

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
JAVA_TOOL_OPTIONS=…  [elided, proxy/truststore line]
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

---

## Question

**In `systems/graph/routes.json` — the largest prose-carrying graph file and the source the L2 route views render from — how many prose clauses assert a categorical absence about a body of evidence, how many of those are false or over-scoped against committed counter-evidence, and what does a whole-field sentinel measure as their blast radius into the committed `systems/views/`?**

It is open because W09b audited JSON *boolean/field* types tree-wide and `artifacts.json` notes; W09d and W09e measured the `publications.json:119` → views path; W09f audited `publications.json`'s `what_it_would_claim` / `why_not_written`. **`routes.json` — 617,198 bytes, 83 records, 4,323 string fields — has never been swept for this defect class**, and W09f's own counter-evidence citations (`routes.json:3693`, `:6584`, `:7894`, `:8109`) show it is the file the other audits reach *into* without auditing.

---

## Prior-work check

```
$ ls research/autonomy/opus-capacity-campaign-20260908/reports/   # 120 reports enumerated
$ grep -n '^##' .../W09b-absence-claim-audit.md .../W09d-... .../W09e-... .../W09f-...
```
Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `systems/POLICY-evidence.md` (head, through §1.2), and reports W09b, W09d, W09e, W09f.

- **W09b** classified ~15 distinct absence-shaped JSON *field types* and 566 categorical prose phrases tree-wide; its conclusion was that the defect had migrated to the summary layer. It did **not** enumerate `routes.json` prose fields.
- **W09d/W09e** are `publications.json:119` → `systems/views/` propagation proofs. I re-used their control-run design, not their subject.
- **W09f** audited `publications.json` `what_it_would_claim` + `why_not_written` (41 fields, 22 categorical clauses). It **cites** `routes.json` as counter-evidence four times but never audits it.
- **W09g** owns the remaining `publications.json` prose fields. I read no part of `publications.json` this run and touched nothing of theirs; their report file landed in the tree during my run (see isolation proof) and I did not open it.

I am not replaying any closed item in `CLOSED-WORK.md`: no retrieval, no source fetch, no NR4A Perspective, no denied-route replay, no clinical claim.

---

## Method / inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `98a0833f` → `84f02dae` | tree under test, read-only |
| `systems/graph/routes.json` (617,198 B; **83 records, 4,323 string fields, 6,100 sentences**) | the source under test |
| `systems/systems_check.py` | the generator actually run (`--write-views`) |
| `systems/views/` (**107 committed files**) | the generated layer, copied to `/tmp/claude-0/w26-views-committed` before any run |
| `/tmp/claude-0/w26/` | scratch copy via `tar --exclude=./.git` (`TAR_EXIT=0`; `cmp` → `ROUTES_IDENTICAL`) |
| `/tmp/claude-0/w26x/scan_absence.py`, `sentinel.py`, `sentinel2.py` | the three scripts I wrote and ran |

Python 3.11 stdlib only. Enumeration: walk every string leaf; split on `(?<=[.!?;])\s+|\n+`; match a 60-term absence regex (W09b/W09f's term set, extended with `does not exist`, `no reachable`, `no published`, `for the first time`, `in the world literature`, `nowhere in`, `zero`); then **hand-classify every hit**, because the regex over-fires on disclaimers, self-scoped statements and ordinary measurements.

Target class, stated so the count means something (W09b's, unchanged): *a clause asserting, about a body of evidence — literature, corpus, archives, registries, cohorts, "anyone", "the field" — that some thing is not recorded, found, reported, built or studied there.* A **disclaimer** ("nothing here asserts efficacy"), a **self-scoped** statement ("nothing in this repository has ever derived copy number from a methylation array") and a **bounded negative** ("no EMC paper in a 272-record open-access corpus reports a phospho-RET measurement") are **not** this class.

---

## Result

### R.1 — The population, and the regex-fires-versus-survives-reading ratio `PRIMARY`

| pass | n |
|---|---|
| records in `routes.json` | **83** |
| string leaf fields | **4,323** |
| sentences after splitting | **6,100** |
| sentences the 60-term absence regex fires on | **218** |
| distinct fields firing | **182** |
| …of those, sentences that are genuinely a negative **about a body of evidence** (bounded or not) | **82** |
| …of those, **CATEGORICAL** (unbounded within their own field) | **45** |
| …**bounded or explicitly self-scoped**, surviving as written | **37** |
| distinct fields carrying ≥1 categorical clause | **~33** |

⭐ **The ratio, which is the finding that keeps this class of audit honest: 218 sentences fire, 82 survive the first reading, 45 survive the second.** 136 of the 218 firings (62%) are *not* absence-of-evidence claims at all. The three dominant false-fire shapes, each quoted:

- **disclaimers** — `RT-HOST-FACTOR.limitations[2]`: *"Nothing in this route asserts efficacy, safety, a therapeutic window or clinical readiness"*; `RT-FUSION-OUTPUT.limitations[7]`, `RT-CART-SURFACE.grade.value` (*"nothing here bears on efficacy in EMC"*), `RT-LIMB-PERFUSION.grade.value` (*"⚠ Nothing here says perfusion works"*);
- **self-scoped statements** — `RT-MTAP-PRMT5.required_validation[2].what`: *"nothing in this repository has ever derived copy number from a methylation array"*; `RT-ALK-HIT.rationale`: *"nothing here has ever followed it up"*;
- **ordinary measurements and zeros** — `RT-ALK-HIT.remaining_unknowns[3]`: *"The DepMap prior over 91 screened sarcoma lines has ALK and ROS1 dependent in ZERO of them"*; `RT-PARTNER-STRAT`'s zero-event arms; `RT-VTE-PROPHYLAXIS.rationale`: *"Zero true VTE deaths appear in the retrieved corpus."*

Counting any of those as an absence claim would be the exact error this task exists to prevent — and the over-fire rate here (62%) is **worse** than in `publications.json` (W09f: 34 fields fire, 17 survive), because `routes.json` carries far more disclaimer and measurement prose per record.

### R.2 — The 45 categorical clauses, classified `PRIMARY`

**Tally: 6 FALSE · 12 OVER-SCOPED · 27 UNVERIFIABLE · (37 further clauses bounded and TRUE as written).**

#### ⛔ FALSE — 6 clauses in 6 fields, refuted by committed evidence inside this same file

| # | record · field · `routes.json:line` | clause, quoted | refutation |
|---|---|---|---|
| 1 | `RT-SGK1.publication.contribution` · **`:6399`** | *"One of four kinase observations … that **nobody has followed up**."* | R.3 |
| 2 | `RT-DNAPK.publication.contribution` · **`:6505`** | identical string | R.3 |
| 3 | `RT-RET.publication.contribution` · **`:6607`** | identical string | R.3 |
| 4 | `RT-ALK-HIT.publication.contribution` · **`:6712`** | identical string | R.3 |
| 5 | `RT-SGK1.rationale` · **`:6415`** | *"…published two decades ago and **never followed up by anyone**."* | R.3 |
| 6 | `RT-METASTASECTOMY.publication.contribution` · **`:8516`** | *"…and the one with **no literature at all**."* | R.4 |

#### ⚠ OVER-SCOPED — 12 clauses in 10 fields

| # | record · field · line | clause, quoted | why |
|---|---|---|---|
| 7 | `RT-ANDGATE.grade.value` · `:3624` | *"⏸ hold — arm-2 chemistry **does not exist**"* | R.5 |
| 8 | `RT-ANDGATE.closure_note` · `:3667` | *"Arm-2 chemistry **does not exist**…"* | R.5 |
| 9 | `RT-ANDGATE.publication.contribution` · `:3672` | *"…the statement of exactly what **does not exist** for it to be built."* | R.5 |
| 10 | `RT-ANDGATE.required_validation[0].what` · `:3698` | *"A ligand for the second arm, **which does not exist**"* | R.5 |
| 11 | `RT-COVALENT-PROBE.closure_note` · `:1166` | *"…which is $0 in-silico work **nobody has done**"* | the clause immediately before it is correctly self-scoped (*"is computed anywhere **in this repo**"*); "nobody has done" silently widens the same negative from the repo to the world |
| 12 | `RT-COVALENT-PROBE.closure_note` · `:1166` | *"…so there is **no published precedent** to copy."* | supported only by a reading of *one* named source campaign ("the source campaign used no purified protein"); no census of the precedent literature is committed |
| 13 | `RT-HORMONE-PARTNER.grade.value` · `:6800` | *"⚠ This is a RETRIEVAL negative, not a measurement: **nobody has asked** whether the human HSPA8 promoter contains an ERE."* | the field *names its own instrument correctly* and then states the conclusion categorically anyway — the smallest possible version of the defect |
| 14 | `RT-HORMONE-PARTNER.grade.value` · `:6800` | *"…is reported in ONE EMC patient **in the world literature**…"* | the paired half (*"ZERO of the 84 partner-genotyped EMC cases across the two cohorts this repository cites — Wilson 95% upper bound 4.4%"*) is exemplary; "the world literature" is not a corpus this repository has enumerated |
| 15 | `RT-HORMONE-PARTNER.remaining_unknowns[1]` · `:6821` | *"…a hormone response element **NOBODY HAS LOOKED FOR**."* | same claim, same missing census |
| 16 | `RT-TRIAL-REACH.grade.value` · `:7939` | *"**No trial anywhere** is indexed to this disease's driver."* | the preceding sentence in the same field bounds it correctly — *"a **registry-wide** term search for it returns five studies of which NOT ONE is an oncology study"*. "anywhere" over-reaches that one registry index |
| 17 | `RT-RISK-MODEL.grade.value` · `:8586` | *"No validated EMC risk model exists — `nomogram` returns zero files repo-wide and **no published EMC series presents one**."* | the evidence offered (`nomogram` repo-wide grep) supports a *repo* negative; the second half is a claim about the publication record with no committed census |
| 18 | `RT-SURGICAL-QUALITY.readiness.why_not_higher` · `:8281` | *"The referral half needs fields **nobody has PUBLISHED**…"* | the same field's preceding sentence is correctly bounded (*"the margin fields are extracted"*); the referral half's negative names no corpus |

#### ❓ UNVERIFIABLE — 27 clauses (no committed census either way)

Representative, with `routes.json` lines: `RT-DEGRADER.remaining_unknowns[2]:159` *"none has been built by anyone"*; `RT-MONOVALENT.remaining_unknowns[0]` *"Nobody has run that assay."*, `.publication.contribution:1359` *"a separate question nobody has asked"*, `.readiness.why_not_higher:1406` *"has never been tested by anyone"*; `RT-SSTR2`, `RT-FAP-RLT`, `RT-TRABECTEDIN`, `RT-JUNCTION-NEOANTIGEN`, `RT-RESPIRATORY-FAILURE`, `RT-HOST-FACTOR` — six instances of *"this has never been measured [in EMC / in this disease]"*; `RT-MDT-LUNG.rationale:7602` *"nobody has assembled those reports or noticed…"* and `.grade.value` *"A CATEGORY ERROR NOBODY HAD NAMED"* / *"nobody has tabulated them"*; `RT-RET.remaining_unknowns[1]` *"the measurement that has never been made in this disease by anyone"* and `.readiness.missing[1]` *"which nobody has published"*; `RT-SGK1.readiness.missing[0]` *"which nobody has made in EMC"*; `RT-MTAP-PRMT5.rationale` *"it has simply never been asked"*; `RT-APOPTOSIS-DEP.rationale` *"nobody has asked which one"*; `RT-GLUE.remaining_unknowns[1]` *"nobody has shown it"*; `RT-ATR-ASSESS.remaining_unknowns[1]` *"a step nobody has validated for this class"*; `RT-CRISPR-CAS13.readiness.why_not_higher` *"a delivery problem the field has not solved"*; `RT-PARTNER-STRAT.rationale` *"no source pools the response data at all"*; `RT-SCHEDULING.remaining_unknowns[1]` *"which no published EMC series reports"*; `RT-RISK-MODEL.remaining_unknowns[2]` and `RT-METASTASECTOMY.remaining_unknowns[1]` *"which no series has tested jointly / assessed"*; `RT-TREATMENT-HARM.remaining_unknowns[0]` *"follow-up nobody has published for this histology"*.

⚠ **Two clauses I deliberately excluded from the class and name so the exclusion is checkable.** `RT-SCHEDULING.required_validation[1].what` and `RT-SEQUENCING.required_validation[1].what` both read *"Prospective confirmation, which no trial in this disease will supply."* That is a **prediction about the future**, not an absence claim about a body of evidence; it fires the regex and does not belong in the count. It is still an unhedged forecast and a reader may want it softened, but that is a different defect and not mine to route.

**Smallest correct restatement — one honest bounded-negative template covers all 27 UNVERIFIABLE clauses**, and this repository already wrote it: `research/modalities/nr4a3_fusion_targets.py:1904-1934` → `⛔_how_to_state_it`, *"a bounded negative about a SEARCH … **AN ABSENT READING IS NOT A READING OF ABSENCE.**"* Concretely, e.g. for `RT-SSTR2.remaining_unknowns[0]`: *"Whether EMC expresses the receptor at all — **no SSTR2 measurement in EMC has been retrieved in the corpora this repository holds, as of 2026-09-08**."* Each substitution is a scope word, not a finding.

### R.3 — The `nobody has followed up` clause is FALSE, and `routes.json` refutes it 185 lines away `PRIMARY`

The identical 135-character string sits at `:6399`, `:6505`, `:6607`, `:6712` — one per kinase route, each asserting the negative about **all four** observations collectively.

`RT-RET.grade.value` at **`routes.json:6584`** records, verbatim:

> *"⭐ AND THE SHARPEST EVIDENCE ON THIS ROUTE WAS FOUND 2026-08-27, IN A PAPER THIS ROUTE HAD NEVER READ: PMID 29937513 (Urbini et al., Int J Mol Sci 2018, PMC6073125, DOI 10.3390/ijms19071855) is by the SAME GROUP as the 2014 activation report — Stacchiotti, Casali, Pantaleo, Dei Tos, Maestro, Dagrada and Pilotti are all authors of both — and its abstract states, verbatim: 'Recently, we reported on the therapeutic activity of sunitinib in a series of EMC cases, however the molecular target of sunitinib in EMC is unknown.'"*

and, in the same field:

> *"…PMID 28423517's introduction, read in full text 2026-08-27, renders it as 'analysis of receptor tyrosine kinase (RTK) activity demonstrated elevated expression and activation of RET…'"*

The originating group published again on the strongest of the four leads, and a second paper restates it in full text. **A follow-up exists, this repository has read it, and it is recorded 185 lines below the clause that denies it.** This is W09f's finding at `publications.json:286` — reproduced here at its *source*: the graph's route layer, not just its publication layer, carries the false clause, four times over.

**Smallest correct restatement** (135 → 178 chars, four identical edits):

> *"One of four kinase observations specific to this disease that exist in the published or curated record and that **no prospective EMC-specific test has followed up** — the RET observation was restated by its originating group in PMID 29937513, which calls the molecular target unknown (`RT-RET` grade)."*

and for `RT-SGK1.rationale:6415`, *"…published two decades ago and **with no follow-up retrieved in this repository's corpora**."* — which is what the sibling route `RT-ALK-HIT.rationale` already says correctly: *"nothing here has ever followed it up."*

### R.4 — `RT-METASTASECTOMY`: the record refutes its own contribution field `PRIMARY`

`:8516` — *"Plausibly the highest-yield survival intervention available in this disease today, and the one with **no literature at all**."*

Its own `grade.value`, in the same record, states:

> *"Local therapy of metastases is meanwhile ALREADY BEING GIVEN in all three curated series — 8 of 29 patients presenting with distant metastases in Masunaga; 8 lung metastasectomies and 2 radiofrequency ablations … among Chiusole's 59 patients …; 5 of the 13 who recurred distantly in Bishop (`research/modalities/emc-site-curation.json`)."*

and, explicitly:

> *"⚠ Superseded, retained (rule 1.2): 'A 554-record open-access corpus retrieved 2026-08-09 contains ZERO EMC records matching metastasectom*… nobody has asked the question in this histology.' **⛔ REFUTED 2026-09-01 BY A FILE INSIDE THAT CORPUS.** … The 'ZERO records' string was a typed literal in the generator and no gate compared it against the corpus; it is now derived (`emc_care_delivery_evidence.py::absence_result`) and reads ⛔ NOT ZERO."*

and `next.best_next_action`: *"'No comparator anywhere in the literature' is also refuted — Bishop reports salvage surgery p = 0.15 at n = 13."*

⭐ **This is W09f's staleness pattern in its purest form: the correction landed in `grade.value` and `next.best_next_action` on 2026-09-01 and never reached `publication.contribution` in the same record.** The route retracted the false absence and left one copy of it standing in the field that renders into `L3-publications.md`.

**Smallest correct restatement:** *"Plausibly the highest-yield survival intervention available in this disease today, and **the one whose only comparison in the reachable literature is uninformative** (Bishop 2019, salvage surgery p = 0.15 at n = 13)."* — which is verbatim the honest form this record's own `next.best_next_action` already prints: *"**The honest statement is that the only comparison in the reachable literature is uninformative.**"*

⛔ No clinical claim: every count above is a count of what was *reported as done*, with no outcome, comparator, rate or recommendation attached. Nothing here asserts efficacy, safety, tolerability or appropriateness of any operation. There is no wet lab.

### R.5 — `RT-ANDGATE`: one record asserting non-existence four times and asking the same question as open once `PRIMARY`

`:3693`, `remaining_unknowns[0]`: *"**Whether any ligand exists** for the EWSR1 half — the second arm's chemistry does not exist."*

Four other fields in the same record state it as settled: `:3624`, `:3667`, `:3672`, `:3698`. W09f judged the `publications.json` twin OVER-SCOPED **by citing `routes.json:3693`** — but `routes.json` is where both forms live, so the graph layer contradicts itself internally, and the publication layer merely inherited the wrong half.

**Smallest correct restatement**, four edits: *"⏸ hold — **no ligand for the EWSR1 half has been retrieved, and whether one exists is open**"* (grade), and correspondingly in `closure_note`, `contribution` and `required_validation[0].what`. This is a two-word change per field and makes all five fields agree with `remaining_unknowns[0]`.

### R.6 — Why `routes.json` is substantially cleaner than `publications.json`, and the structural reason `PRIMARY`

**It is cleaner, and the reason matters more than the count.** Rates, for the fields each audit examined:

| file | categorical clauses examined | FALSE | OVER-SCOPED | defective share |
|---|---|---|---|---|
| `publications.json` (W09f) | 22, in 41 fields | 4 | 6 | **10/22 = 45%** |
| `routes.json` (this audit) | 45, in 4,323 fields | 6 | 12 | **18/45 = 40%**, but **18 clauses in 6,100 sentences = 0.30%** |

Three structural reasons, each evidenced:

1. **`routes.json` states the governing rule inside its own prose, and applies it.** `RT-DNAPK.grade.value`: *"That is an **ABSENT READING AND NOT A READING OF ABSENCE** — nothing here says the catalytic subunit is or is not a dependency"*; `RT-DNAPK.remaining_unknowns[0]`: *"⚠ Still an ABSENT READING"*; `RT-LIMB-PERFUSION.grade.value`: *"That is an absent reading, NOT a reading of absence."* The file self-polices in three separate records. `publications.json` never states the rule.
2. **`routes.json` habitually bounds its negatives with a named corpus, a count and a date, and then names the boundary explicitly.** The exemplar, `RT-LIMB-PERFUSION.grade.value`: *"Two independent PubMed queries return ZERO records … against a 468-record disease literature and a 444-record limb-perfusion-in-sarcoma literature, with an instrument control run in the same session"*, followed by *"⚠ AND THE NULL HAS A BOUNDARY — a field search cannot see a per-patient histology table, so 'nobody has published a perfusion report ABOUT this disease' is established while 'no such patient has ever been perfused' is not, **and is not claimed**."* Likewise `RT-RET.supporting_evidence[2]`: *"no EMC paper in a 272-record open-access corpus reports a phospho-RET or ligand measurement"*; and `RT-FUSION-OUTPUT.grade.value`, which carries the sentence W09f judged OVER-SCOPED in `publications.json` — *"no experiment has measured where an NR4A3 fusion binds…"* — but here appends, **in the same field**, *"— a bounded statement about what has been deposited under a label an archive indexes, not a claim that no such data exists"*, plus the 2026-08-08 sweep of GEO, SRA, BioProject, BioSample, ArrayExpress, ENA and ChIP-Atlas that backs it. **The identical sentence is OVER-SCOPED in `publications.json` and TRUE in `routes.json`, and the only difference is the clause that follows it.** That is the whole finding in one comparison.
3. **`routes.json` retains superseded false absences under `rule 1.2` rather than deleting them**, so its own history of this defect is visible: `RT-RT-INTENSIFY.grade.value` — *"⚠ Superseded, retained (rule 1.2): 'carbon ion appears nowhere in it across a 354-paper open-access corpus…' ⛔ THAT WAS A FALSE ABSENCE, AND ITS OWN CORPUS REFUTES IT"* (W09b's C1, landed here); `RT-METASTASECTOMY` (R.4); `RT-VACCINE-COMBINATION.remaining_unknowns[2]` — *"⚠ SUPERSEDED WORDING, RETAINED: 'which is unmeasured in this disease' — it was already false when written."*

⭐ **And the structural difference that explains the residue.** W09f's diagnosis was that `publications.json`'s prose fields "have no row to be scoped by". `routes.json` prose fields *do* sit on a row — a named route — so the disease, the modality and the instrument are all supplied by context, and most negatives inherit a real scope for free. **The 18 defective clauses are concentrated in exactly the fields where the row's scope does not help**: five of the six FALSE clauses are `publication.contribution`, a field that describes what a *paper* would say and therefore ranges over the literature rather than over the route; and the OVER-SCOPED ones are the clauses that reach past the route's own boundary — from "this repo" to "nobody" (`RT-COVALENT-PROBE`), from "the registry index" to "anywhere" (`RT-TRIAL-REACH`), from "repo-wide" to "no published series" (`RT-RISK-MODEL`), from "extracted" to "published" (`RT-SURGICAL-QUALITY`). **The defect is not distributed across the file; it is the seam where a route-scoped field starts talking about the world.**

### R.7 — Measured blast radius, by whole-field sentinel and regeneration `PRIMARY`

Sixteen sentinels (12 + 4), each: assert the field's value, substitute `ZZSENTINELZZ`, re-serialize, regenerate, walk **all 111 written view files including `registers/`**, count sentinel occurrences and unified-diff ±lines against the committed set, restore pristine from `/home/user/Rare-cancers`, regenerate, and **assert the restore is a no-op**. Every `gen_exit=0`, every stdout `systems_check: wrote 111 view(s) to systems/views/`, final `ALL_RESTORED_OK`, `SCRIPT_EXIT=0` / `SCRIPT2_EXIT=0`.

| record · field · `routes.json:line` | class | files touched | committed lines consumed | sentinel occurrences | exit |
|---|---|---|---|---|---|
| `RT-SGK1.publication.contribution` `:6399` | FALSE | **2** — `L2-rt-sgk1.md:97`, `L3-publications.md:444` | 2 | 2 | **0** |
| `RT-DNAPK.publication.contribution` `:6505` | FALSE | **2** — `L2-rt-dnapk.md:100`, `L3-publications.md:442` | 2 | 2 | **0** |
| `RT-RET.publication.contribution` `:6607` | FALSE | **2** — `L2-rt-ret.md:99`, `L3-publications.md:443` | 2 | 2 | **0** |
| `RT-ALK-HIT.publication.contribution` `:6712` | FALSE | **2** — `L2-rt-alk-hit.md:101`, `L3-publications.md:441` | 2 | 2 | **0** |
| `RT-SGK1.rationale` `:6415` | FALSE | **1** — `L2-rt-sgk1.md:52` | 1 | 1 | **0** |
| `RT-METASTASECTOMY.publication.contribution` `:8516` | FALSE | **2** — `L2-rt-metastasectomy.md:88`, `L3-publications.md:517` | 2 | 2 | **0** |
| `RT-ANDGATE.grade.value` `:3624` | OVER-SCOPED | **1** — `L2-rt-andgate.md:23` | 1 | 1 | **0** |
| `RT-ANDGATE.closure_note` `:3667` | OVER-SCOPED | **1** — `L2-rt-andgate.md:129` | 1 | 1 | **0** |
| `RT-ANDGATE.publication.contribution` `:3672` | OVER-SCOPED | **2** — `L2-rt-andgate.md:98`, `L3-publications.md:104` | 2 | 2 | **0** |
| `RT-ANDGATE.required_validation[0].what` `:3698` | OVER-SCOPED | **1** — `L2-rt-andgate.md:67` | 1 | 1 | **0** |
| `RT-COVALENT-PROBE.closure_note` `:1166` | OVER-SCOPED | **1** — `L2-rt-covalent-probe.md:144` | 1 | 1 | **0** |
| `RT-HORMONE-PARTNER.grade.value` `:6800` | OVER-SCOPED | **1** — `L2-rt-hormone-partner.md:23` | 1 | 1 | **0** |
| `RT-HORMONE-PARTNER.remaining_unknowns[1]` `:6821` | OVER-SCOPED | **1** — `L2-rt-hormone-partner.md:58` | 1 | 1 | **0** |
| `RT-TRIAL-REACH.grade.value` `:7939` | OVER-SCOPED | **1** — `L2-rt-trial-reach.md:23` | 1 | 1 | **0** |
| `RT-RISK-MODEL.grade.value` `:8586` | OVER-SCOPED | **1** — `L2-rt-risk-model.md:23` | 1 | 1 | **0** |
| `RT-SURGICAL-QUALITY.readiness.why_not_higher` `:8281` | OVER-SCOPED | **1** — `L2-rt-surgical-quality.md:76` | 1 | 1 | **0** |

**Totals for a complete landing of all 18 defective clauses: 16 source fields → 21 committed view lines across 13 view files** (12 `L2-rt-*.md` + `L3-publications.md`, which alone consumes 5 lines: `:104`, `:441`, `:442`, `:443`, `:444`, `:517`).

⭐ **On the 150-character clip: it does not fire anywhere in this file, and I measured that rather than assuming it.** In `publications.json` (W09f) a `_clip(gap, 150)` in `L3-publications.md` meant a clause-level fix changed *fewer* lines than the whole-field sentinel. Here, every audited field renders in full:

| field | field length | offending-clause offset | rendered line length | clause present in rendered line | line truncated (`…`) |
|---|---|---|---|---|---|
| `RT-RISK-MODEL.grade.value` | **2,605** | 1,519 | 2,679 | ✅ yes | ❌ no |
| `RT-HORMONE-PARTNER.grade.value` | 1,830 | **1,710** | 1,955 | ✅ yes | ❌ no |
| `RT-TRIAL-REACH.grade.value` | 1,694 | 819 | 1,857 | ✅ yes | ❌ no |
| `RT-SURGICAL-QUALITY.readiness.why_not_higher` | 719 | 657 | 719 | ✅ yes | ❌ no |
| `RT-COVALENT-PROBE.closure_note` | 475 | 297 | 496 | ✅ yes | ❌ no |
| `RT-SGK1.publication.contribution` | 135 | 112 | 163 | ✅ yes | ❌ no |
| `RT-METASTASECTOMY.publication.contribution` | 121 | 100 | 149 | ✅ yes | ❌ no |
| `RT-SGK1.rationale` | 221 | 193 | 221 | ✅ yes | ❌ no |

**Consequence for the lander: in `routes.json`, sentinel radius = clause-level-fix radius, exactly.** Every one of the 21 lines the sentinels consumed is a line a clause-level correction also rewrites. The only truncation visible on any affected row is in `L3-publications.md`'s *first* column — the route display name, clipped at 60 (`_clip(disp, 60)`, `systems_check.py:3852`), e.g. *"Pulmonary metastasectomy as a decision rather than a"* — which no correction to these fields touches. ⚠ A lengthening restatement (all of R.3–R.5's are longer than what they replace) will renumber lines below the edit within each view; the lander should regenerate and re-diff rather than reuse these numbers.

⭐ **Blast radius is an order of magnitude tighter here than in `publications.json`, for the same structural reason as R.6.** W09f measured 2–7 files and up to 16 committed lines per field, because a `publications.json` field fans out to every L2 route that record claims. A `routes.json` field belongs to one route and renders into that route's own L2 page — one line, once — with `publication.contribution` the sole field that also reaches `L3-publications.md`. **Fixing 18 defective clauses in the file the L2 views render from is a 16-field, 21-line change.** That is a small, checkable landing, not a sweep.

---

## Validation evidence

Environment for every run: scratch copy at `/tmp/claude-0/w26/`, produced by `tar --exclude=./.git -cf - . | tar -xf - -C /tmp/claude-0/w26/` from `/home/user/Rare-cancers` (`TAR_EXIT=0`; `cmp` on `routes.json` → `ROUTES_IDENTICAL`). Committed views snapshotted to `/tmp/claude-0/w26-views-committed` (**107 files**) before any generator run. Linux, Python 3.11 stdlib, no network.

### `RUN` — Enumeration
```
$ python3 /tmp/claude-0/w26x/scan_absence.py
records 83 string fields 4323 sentences 6100
regex-firing sentences 218
distinct fields firing 182
    55 /remaining_unknowns/[]      38 /grade/value        21 /rationale
    18 /required_validation/[]/what                       14 /readiness/why_not_higher
    11 /closure_note               11 /publication/contribution
    10 /readiness/missing/[]        9 /timing/rationale    8 /distinct_from/[]/why
     8 /next/best_next_action       5 /supporting_evidence/[]/what_it_supports
     4 /limitations/[]              3 /timing/two_year_delta   3 /timing/six_month_delta
```
All 218 sentences were printed in full and read by hand; the classification in R.2 is mine, not the script's.

### `RUN` — Control: regeneration with no edit is a no-op
```
$ cd /tmp/claude-0/w26 && python3 systems/systems_check.py --write-views
systems_check: wrote 111 view(s) to systems/views/
GEN_EXIT=0
$ diff -rq /tmp/claude-0/w26-views-committed /tmp/claude-0/w26/systems/views
CONTROL_DIFF_EXIT=0
```
Idempotent at this HEAD, so every later diff is attributable to the sentinel alone. (The generator reports 111 written views while the committed tree holds 107 files — the same accounting W09f recorded; the control diff proves the written set is byte-identical to the committed one.)

### `RUN` — Second control: re-serializing `routes.json` changes no view
```
RESERIALIZE_CONTROL gen_exit=0 stdout='systems_check: wrote 111 view(s) to systems/views/'
                    changed_files=0 +0/-0 sentinel_occ=0
```
Run at the head of both sentinel scripts. This is required because my sentinel writes the file back with `json.dump(indent=2, ensure_ascii=False)`; the control proves that re-serialization alone is view-invisible, so nothing in R.7 is a formatting artifact.

### `RUN` — Sixteen whole-field sentinels
`/tmp/claude-0/w26x/sentinel.py` (12 cases, `SCRIPT_EXIT=0`) and `/tmp/claude-0/w26x/sentinel2.py` (4 cases, `SCRIPT2_EXIT=0`). Each iteration restores the pristine file from `/home/user/Rare-cancers`, regenerates, and **asserts the restored state produces zero changed files** before proceeding; both scripts ended `ALL_RESTORED_OK`. Verbatim per-case output is transcribed into R.7's table; every `gen_exit` was `0` and every stdout was `systems_check: wrote 111 view(s) to systems/views/`.

### `RUN` — Clip-offset measurement
The R.7 clip table, computed by locating each clause's character offset in the source field and comparing against the rendered view line. No `…` appears in any of the 21 affected lines.

### `RUN` — Isolation proof
```
$ git status --porcelain   (start) -> empty      (end) -> empty
$ cmp /home/user/Rare-cancers/systems/graph/routes.json /tmp/claude-0/w26/systems/graph/routes.json
ROUTES_STILL_IDENTICAL
$ diff -rq /home/user/Rare-cancers /tmp/claude-0/w26 --exclude=.git   (DIFF_EXIT=1)
Only in .../opus-capacity-campaign-20260908: SAFETY-EVENTS.md
Only in .../opus-capacity-campaign-20260908: executed-artifacts
Only in .../reports: W02g, W04f, W05g, W09g, W12f, W16e, W17i, W18b, W19h, W20h, W21c
```
No difference in `systems/graph/`, `systems/views/`, `systems/systems_check.py`, or anything else. The extra entries are the coordinator's concurrent collections.

### `PROPOSED (NOT RUN)`
- **Correction diffs for the 18 clauses.** Only the *sentinel* radius was measured; R.3–R.5's restatements were not applied and re-diffed, because all three are longer than what they replace and the lander must regenerate anyway. **The claim that clause-level radius equals sentinel radius here is derived from measured clip offsets, not from an applied edit.**
- **Acceptance tests.** Shape only: any gate must assert the superseded sentence is *quoted-and-superseded* inside `⚠ Superseded, retained (rule 1.2): "…"`, never *absent* — a bare `grep` fires on the retained quotation. This file already contains four such retained quotations (R.6 §3) that would break a naive gate. Not written, not run.
- **Adjudicating the 27 UNVERIFIABLE clauses.** Each needs either a committed census or a scope word. Deciding which needs the graph's owner; no retrieval is authorised here and none was attempted.
- `scripts/preflight.sh` — forbidden by dispatch, and no edit exists to gate.
- **Landing anything.** Nothing was applied to the repository.

---

## Limitations

- **The 45/218 split is my reading, not a measurement.** The regex is reproducible; the classification is judgement. I have named every clause with a file and line so each call is checkable and reversible.
- **UNVERIFIABLE means unverifiable in both directions.** I am not asserting those 27 clauses are false. With no network and no committed census, *"nobody has run that assay"* is neither confirmed nor refuted here — which is exactly why the honest form is a bounded negative about a search rather than a claim about the world.
- **`RT-FUSION-OUTPUT`'s archive sweep is quoted, not re-run.** I read the committed record of a 2026-08-08 sweep of seven archives; I did not repeat it, and CORPUS-CONTEXT's rule stands — a listing is not proof of local availability.
- **I did not audit `routes.json`'s non-string structure**, the `registers/` view subdirectory's other sources, or any file outside `routes.json` except as counter-evidence. `publications.json` is W09g's and I did not read it.
- **Blast radius is measured at `98a0833f`/`84f02dae` only.** Generator or schema changes would move these line numbers.
- ⛔ **No clinical claim anywhere.** Nothing here asserts efficacy, safety, selectivity, therapeutic window, tolerability or clinical readiness for any agent, operation or pathway; every count quoted is a count of what was *reported*, with no outcome or comparator attached. There is no wet lab, and no computational result in this repository can establish EMC efficacy.

---

## Stop condition

**Set up front:** return the moment (a) every prose field in `routes.json` is enumerated and sentence-split, (b) every regex-firing sentence is hand-classified as in-class or out-of-class, (c) every in-class categorical clause carries a TRUE/FALSE/OVER-SCOPED/UNVERIFIABLE verdict with the smallest correct restatement for each non-TRUE one, and (d) blast radius is measured by sentinel + regeneration for every FALSE/OVER-SCOPED field with a no-edit control first and real exit codes throughout — or ~40 tool calls / ~40 minutes, whichever came first.

**MET, on the work condition, before the budget.** (a) 4,323 fields, 6,100 sentences; (b) 218 firings read individually; (c) 45 categorical clauses classified, 6 FALSE / 12 OVER-SCOPED / 27 UNVERIFIABLE, restatements given for all FALSE and OVER-SCOPED and one template for the UNVERIFIABLE set; (d) 16 sentinels, two controls, all exits 0, all restores asserted clean.

---

## Tool-call and wall-clock count actually used

**30 tool calls** (target ~40). **Wall clock 5 minutes 48 seconds**, `03:13:18Z` → `03:19:06Z` (target ~40 minutes). Nothing padded; returning on the stop condition.

---

## Next concrete action

**Land the six FALSE clauses only, as one commit, and leave the twelve OVER-SCOPED for a separate decision.** The FALSE set is fully evidenced from inside `routes.json` itself, needs no retrieval, and is a **6-field, 11-line change in 6 view files**: edit `routes.json:6399`, `:6505`, `:6607`, `:6712` (the four identical kinase `publication.contribution` strings) and `:6415` to R.3's restatement, and `:8516` to R.4's — which is verbatim the honest sentence the same record's own `next.best_next_action` already prints. Then run `python3 systems/systems_check.py --write-views` and confirm the diff is exactly `L2-rt-sgk1.md`, `L2-rt-dnapk.md`, `L2-rt-ret.md`, `L2-rt-alk-hit.md`, `L2-rt-metastasectomy.md` and `L3-publications.md` (rows `:441`–`:444`, `:517`), with line numbers re-derived after the edit because all six restatements lengthen their field. ⚠ Do not hand-edit any file under `systems/views/`. ⚠ `RT-METASTASECTOMY`'s fix should quote-and-retain under rule 1.2, matching the four retentions already in this file, or the retained quotation will trip any grep-based gate written later.
