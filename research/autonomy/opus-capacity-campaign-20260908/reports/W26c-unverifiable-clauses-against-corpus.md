<!-- collected 2026-09-08T03:51:46Z by campaign coordinator; agent id a2e4f84e40be30d3c; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a2e4f84e40be30d3c.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

- **Worker:** W26c, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: successor to W26b — corpus adjudication of W26b's 29 UNVERIFIABLE categorical absence clauses in `systems/graph/*.json`.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model (`AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_CODE_VERSION=2.1.42` are harness versions). The coordinator must extract the runtime model from the transcript.
- **Write isolation honoured.** Nothing written, moved or deleted under `/home/user/Rare-cancers`; no git write operation; `scripts/preflight.sh` not run; no repair authored or applied. Nothing written to the frozen corpus (`find … -newermt "2026-09-08 02:35" -type f` → **0**). All execution under `/tmp/claude-0/w26c/`, **deleted before returning** (`REMOVED /tmp/claude-0/w26c`, then `ls` → `No such file or directory`).
- ⚠ **Timing disclosure:** the coordinator's constraint block arrived mid-run, so my `date -u` / `git rev-parse` / `env` capture is at **03:43:06Z**, not at my true first tool call (~03:38Z). Everything before that point was read-only Bash on the live tree and the corpus.
- No network, no retrieval, no paid API, no GPU, no human contact, no publication. No clinical, efficacy, safety, selectivity or readiness claim; there is no wet lab.

`date -u` — recorded start `Tue Sep 8 03:43:06 UTC 2026`, end `Tue Sep 8 03:47:52 UTC 2026`.
`git rev-parse HEAD` — start `5ae0fa04ff9516ac8f820381079d644a094f4a77`, end `e5d60db79f9dcbe7a4b2e6b0db1de6e32ccf69e7`.
`git status --porcelain` — **0 lines at start, 0 at end.**

⚠ **HEAD moved under me and I re-verified rather than assumed.** At end, every value I quote from the live tree was re-read: `census-route-expression-grading.json` `RT-ARGININE.genes.ASS1[GSE24369].readable` → `True`; `RT-MTAP-PRMT5.verdict` → `"SUPPORTED, WITH THE LOCUS READ POWERED ON ONE PLATFORM ONLY."`; `RT-APOPTOSIS-DEP.genes` → `['MCL1','BCL2L1','BCL2','BAX','PMAIP1']`; `curves_supplied` present in `emc-ipd-survival.json`. All unchanged.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0), verbatim except five long proxy/JVM lines marked elided:

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
JAVA_TOOL_OPTIONS=…  [elided, truststore + proxy flags]
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

**For each of W26b's 29 UNVERIFIABLE categorical absence clauses, does the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/` contain evidence that moves it to TRUE, to FALSE, or leaves it UNVERIFIABLE?**

Open because W26b worked only from the live checkout and never opened the corpus; its own limitation says *"29 clauses may each be perfectly true. Their defect is that this repository cannot show it."* That is a claim about what can be shown, and it was made without reading the 5,996-file snapshot — **2,201 of whose files are not present in the live checkout at all**.

---

## Prior-work check

Read in full: `COMMON-BRIEF.md` (including the 03:36Z correction and the "Known, measured, and NOT worth rediscovering" section), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, and `reports/W26b-remaining-graph-files-sweep.md` (43 KB, read entire).

- **Not replayed:** W26b's 3 FALSE and 13 OVER-SCOPED grades — not re-graded. Its 16 sentinels and all blast-radius measurements — not re-run. `publications.json` / `routes.json` (W09f, W26) — not touched. `reports/W25-*` — **not read, not referenced**.
- **Corpus-vs-live file diff, run:** `find corpus -type f | 5996`; per-file existence test against `/home/user/Rare-cancers/` → **2,201 corpus files absent from the live checkout** (e.g. the whole of `research/autonomy/nr4a3-program-source-2026-09-07/` and `nr4a3-program-tissue-2026-09-07/`). This is the surface W26b did not have.
- **Root discipline observed:** every search below was run with cwd `/tmp/claude-0/frozen-corpus/extracted/corpus`, never `.../extracted/`.
- Campaign reports were not used as evidence. Every counter-citation below is a committed or snapshot **data/manuscript** file, quoted by path.

---

## Method / inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `5ae0fa04` → `e5d60db7` | the clauses under test, read-only |
| `/tmp/claude-0/frozen-corpus/extracted/corpus/` (5,996 files, 236 MB) | the evidence body searched |
| `reports/W26b-remaining-graph-files-sweep.md` | the 29-clause list being adjudicated |

Procedure per clause: (1) recover the clause verbatim from the live graph JSON by walking every string leaf of its record; (2) identify the concrete proposition (a gene, a count, a document, a requirement); (3) `grep -rn` that proposition across the corpus, restricted where useful to `research/modalities`, `research/manuscripts`, `research/literature`, `systems`; (4) read the hit and grade. Python 3.11 stdlib, Linux, no network.

⚠ **Clause-count discrepancy, stated rather than smoothed.** W26b's R.2 UNVERIFIABLE paragraph enumerates **30** clauses, and one of them — `blockers.json` `BLK-FUNCTIONAL-ACTIONABILITY.statement_about` — is *also* graded OVER-SCOPED in its R.7 sentinel table. I adjudicate all 30 and flag that one as double-listed; my denominators below are out of 30.

---

## Result

### R.1 — Adjudication summary `PRIMARY`

| new verdict | n / 30 | what the corpus supplied |
|---|---:|---|
| ⛔ **FALSE** (refuted by a snapshot file) | **11** | a committed EMC-tissue expression grading, a site curation, a selectivity specification |
| ⚠ **OVER-SCOPED** (partial committed count exists) | **3** | a dated per-source figure census; an in-repo record of external benchmark sets |
| ❓ **UNVERIFIABLE, unchanged** | **16** | searched, nothing found — reported as a search, not as an absence |

⭐ **The headline: 14 of 30 clauses that W26b could not move are movable, and 11 are outright false.** W26b's diagnosis ("a stating defect, not a scientific one") is wrong for a third of the class. The single artifact responsible for 8 of the 11 is `research/modalities/census-route-expression-grading.json`, which grades **16 census routes against EMC tumour-tissue expression on two platforms** — GPL6244 (6 EMC vs 29 comparator sarcomas) and GPL3290 (10 EMC vs 6 comparator). It is present in **both** the corpus and the live tree; W26b simply did not open it.

### R.2 — The 11 refuted clauses `PRIMARY`

Every path below resolves under `corpus/` and, where noted, also in the live checkout.

| # | record · field | clause, quoted | corpus search run | evidence, quoted | verdict |
|---|---|---|---|---|---|
| 1 | `modalities.json` `MOD-ARGININE-DEPRIVATION.requires[0]` | *"silencing of the argininosuccinate synthase locus in EMC, **which is unmeasured**"* | `grep -rn "\bASS1\b" research systems scripts` | `research/modalities/census-route-expression-grading.json` `routes.RT-ARGININE`: `ASS1` `readable: true` on **both** platforms — `emc_mean_z 1.3492`, `emc_array_percentile 0.9152` (GPL6244); `-0.2579`, `0.4053` (GPL3290). Route `verdict`: *"AGAINST — the selecting feature is absent at transcript level on both platforms."* | ⛔ **FALSE** |
| 2 | `MOD-PRMT5-MAT2A.requires[0]` | *"co-deletion of the MTAP locus, **which is unmeasured in EMC**"* | `grep -rn "\bMTAP\b" …` | same file, `routes.RT-MTAP-PRMT5`, genes `MTAP, CDKN2A, CDKN2B, PRMT5, MAT2A`, `verdict`: *"SUPPORTED, WITH THE LOCUS READ POWERED ON ONE PLATFORM ONLY."* | ⛔ **FALSE as written** — the locus **is** read; what is unmeasured is *copy number*, and the same file's `_language_discipline` already says *"A transcript level is not … a copy number."* |
| 3 | `MOD-PRMT5-MAT2A.rationale` | *"The question is cheap and binary, and **it has simply never been asked**."* | as above | it was asked and answered on 2 platforms; `pinned_figures_quoted_by_the_preprint` carries `mat2a_percentile_gpl6244: 99`, `gpl3290: 84`, `prmt5_percentile_gpl6244: 91`, `gpl3290: 59` | ⛔ **FALSE** |
| 4 | `MOD-MCL1-BCLXL.rationale` | *"…the signature of dependence on a different anti-apoptotic family member. **Nobody has asked which one.**"* | `grep -rn "\bMCL1\b\|\bBCL2L1\b" …` | same file, `routes.RT-APOPTOSIS-DEP` — `selecting_feature`: *"an anti-apoptotic guardian other than BCL-2 holding the threshold"*, genes `MCL1, BCL2L1, BCL2, BAX, PMAIP1`, `verdict`: *"AGAINST AT THE ABUNDANCE LEVEL — no guardian is dominant, and the one that is up is a sensitiser rather than a guardian."* | ⛔ **FALSE** — the question is exactly what that route asks |
| 5 | `MOD-RET.rationale` | *"Nothing here says the receptor is inactive in EMC; it says **nobody has measured it**"* | `grep` RET in the grading file | `routes.RT-RET` — `RET` `readable: true` both platforms (`emc_mean_z 0.2235`, pct `0.5763`; `1.2085`, pct `0.8563`), plus `GDNF/GFRA1/ARTN/NRTN`; `verdict`: *"SPLIT — receptor supported, ligand-dependent activation route weakened."* | ⛔ **FALSE for expression.** Smallest correct restatement: *"…it says **the receptor is measured and present (RT-RET, split verdict) while its activation state is unmeasured**"* |
| 6 | `MOD-TF-LBD-OCCUPANCY.rationale` | *"…pays for that with **a requirement nobody has sized**: how much paralogue selectivity occupancy alone would need."* | `find . -name "*selectivity-requirement*"` | `research/manuscripts/degrader/selectivity-requirement-sizing.md:1-30` — `id: DOC-SELECTIVITY-REQUIREMENT-SIZING`, *"Sizing the selectivity requirement for the three routes that carry `BLK-UNSIZED-REQUIREMENT`"* (`RT-MONOVALENT`, `RT-TCIP`, `RT-ASYMMETRIC`; `date: 2026-08-07`). And `blockers.json` `BLK-UNSIZED-REQUIREMENT.kind_history[0].why`: *"The absent-specification half is retired: selectivity-requirement-sizing.md states the requirement … as nine rows with quantity, comparator and asymmetry-correct pair form."* | ⛔ **FALSE**, refuted by the repository's own blocker record |
| 7 | `strategies.json` `ST-REPURPOSING.limitations[1]` (first half) | *"Several routes here rest on a direction of effect that **has never been read in EMC tissue**"* | as R.2 #1 | `census-route-expression-grading.json` `_what`: *"Verdicts for the modality-census routes whose selecting feature was ALREADY readable in `emc-expression-panels.json`."* **16 routes graded**, each against its own `direction_the_route_needed` | ⛔ **FALSE** |
| 8 | `ST-REPURPOSING.limitations[1]` (second half) | *"an expression readout would settle them cheaply and **does not exist**"* | as above | the readout exists (`emc-expression-panels.json`, live; the grading file, corpus + live) and has already settled 16 routes | ⛔ **FALSE** |
| 9 | `ST-RADIOLIGAND.limitations[0]` | *"**Target expression in EMC is unmeasured**; the case is currently inherited from neuroendocrine and stromal biology rather than observed in this disease."* | `grep -rn "SSTR2" research/modalities research/manuscripts research/literature systems` | `research/modalities/emc-tissue-read-statistics.json` (corpus + live) `primary.GPL6244.SSTR2`: `delta -0.0424, p 0.707208, ci -0.3127…0.2279, n_emc 6, n_comparator 29, significant false`. `research/modalities/gse28866-tumour-vs-normal.json` `SSTR2`: `emc_median 0.35226…, normal_median 0.22813…, sarcoma_median 0.25671…, _n_emc_libs 4`; ratio block `emc_over_normal 1.5441 (pct 89.2)`, `emc_over_sarcoma 1.3722 (pct 84.0)`. `research/autonomy/nr4a3-program-tissue-2026-09-07/analysis-config.json` (**corpus-only**) lists `SSTR2` first in `previously_exposed_gene_exclusion`. | ⛔ **FALSE.** Smallest correct restatement: *"Target expression in EMC is measured and **null**: SSTR2 shows no EMC-vs-comparator difference on GPL6244 (Δ −0.042, p 0.71, n 6 vs 29) — the family's case is a negative reading, not an absent one."* |
| 10 | `ST-MICROENV.limitations[2]` | *"The matrix **has never been measured in this disease as a therapeutic compartment** — only described histologically"* | `grep -rln "sulfate-donor\|glycosaminoglycan" research systems` | grading file `routes.RT-MATRIX-SYNTHESIS` (genes `CHST11, CHST14, PAPSS1, PAPSS2, XYLT1`; verdict *"AGAINST AS STATED"*) and `routes.RT-MATRIX-ADDRESS` (genes `CHST11-14`; verdict *"NOT SUPPORTED ON CAPACITY"*) — the CS-biosynthetic and sulfate-donor machinery read in EMC tissue precisely as a therapeutic compartment | ⛔ **FALSE**, and the same record's own `next.best_next_action` already contradicts it: *"Grade the glycosaminoglycan and sulfate-donor expression read **that is already committed here**"* |
| 11 | `ST-LOCOREGIONAL.limitations[0]` | *"every route here is limited to a subset of patients **whose size has not been established in this disease**"* | `python3` walk of `research/modalities/emc-site-curation.json` (corpus + live) | `pooled_extremity_fraction.extremity_strict`: `events 194 / denom 271 = 71.6%`, Wilson 95% `65.9–76.6`, per cohort `chiusole2020 78.0 / masunaga2025 67.8 / bishop2019 78.0` | ⛔ **FALSE for the anatomically-confined-primary subset.** Smallest correct restatement: *"…limited to a subset whose size is established for extremity primaries (194/271 = 71.6% [65.9–76.6], `emc-site-curation.json`) and **is not poolable for the lung-confined metastatic pattern**, which that file's `⛔_no_pooled_estimate` block refuses to estimate."* |

### R.3 — The 3 clauses that move to OVER-SCOPED `PRIMARY`

| # | record · field | clause | corpus evidence | why not FALSE |
|---|---|---|---|---|
| 12 | `forecasts.json` `FC-RECONSTRUCTED-IPD.scenarios.conservative.rationale` | *"That is the live failure mode and **nobody has counted the tables**."* | `research/modalities/emc-ipd-survival.json` (corpus + live): `candidate_sources` = **17 entries**, of which **5 carry `figure_checked: true` with a `figure_finding` block**, several with a dated `risk_row_measured_2026_08_27` field. Two positives (`stacchiotti2013anthracycline`: *"present — five marks under the axis, aligned with all five tick labels"*, `numbers_at_risk_row: True`; `morioka2016trabectedin`: *"present, and READ"*), three negatives (`chiusole2020` *"absent (all four figures)"*, `masunaga2025`, `martinbroto2020immunosarc1`). | a partial, dated count over the **reachable** set exists; no count over "published EMC series" does. Fix is one scope phrase: *"…and **the count is partial: 5 of 17 candidate series measured (2026-08-27), 2 positive, 3 absent**."* |
| 13 | `technologies.json` `TECH-RECONSTRUCTED-IPD.evidence[1]` | *"…how many EMC series print a numbers-at-risk table, **which nobody has counted**."* | same | same |
| 14 | `forecasts.json` `FC-FE-CRYPTIC-POCKET.scenarios.optimistic.rationale` | *"The ingredients exist; **nobody has assembled them into a benchmark**."* | `research/modalities/instrument-options.json:~236` (IC-4, `known_answer_test.external_option`): *"held-out cryptic-site benchmark sets (**CryptoSite / PocketMiner-class**) — availability and licence UNVERIFIED here; a $0 CI check settles it"* | the repository's own record says such benchmark sets exist externally; what is unassembled is the *specific* conjunction the clause imagines (a cryptic-pocket set paired with an ML-potential engine). Fix: *"…nobody has assembled them into a benchmark **of the kind this needs — cryptic-site sets of the CryptoSite/PocketMiner class exist (`instrument-options.json`, IC-4), with no ML-potential engine attached**."* |

### R.4 — The 16 that remain UNVERIFIABLE, with the search that was run `PRIMARY`

**These are searches, not absences.** Each row states what I looked for; a null here means the corpus snapshot did not answer it, never that the repository or the literature is silent.

| record · field | clause | search run | outcome |
|---|---|---|---|
| `blockers.json` `BLK-FUNCTIONAL-ACTIONABILITY.statement_about` ⚠ *also graded OVER-SCOPED by W26b* | *"a functional cell assay **nobody has run**"* | `grep -rln "dTAG" research systems` | 6 files; `research/modalities/nr4a3-degrader-design-spec.md:265` records the dTAG test as *"the wet-lab hand-off"*, `depmap-insilico-findings.md:75` *"the make-or-break"*. No assay, no result. **UNVERIFIABLE — and correctly so: there is no wet lab.** |
| `BLK-NO-FIELD-ATTENTION-MEASUREMENT.name` | *"a corpus-wide term census **nobody has run**"* | `grep -rn "term census" research systems` | hits confirm the census is a named, untaken, $0 in-repo action; `emc-care-delivery-evidence.json:101` refutes a *different* zero (*"NOT ZERO -- REFUTED 2026-09-01"* for `metastasectom`). No census output. **UNVERIFIABLE** |
| `BLK-UNSIZED-REQUIREMENT` × **3** | *"three **unmeasured** dose-responses"* | as clause 6 | the corpus confirms the *specification* landed and that what remains is three bench dose-responses. Nothing measures them. **UNVERIFIABLE** |
| `forecasts.json` `FC-EMC-EXPRESSION-DATA` | *"neither is on **anyone's** published roadmap"* | grep for roadmap/deposition census | no census of external roadmaps in the corpus. **UNVERIFIABLE** |
| `FC-E3-RECRUITER-STRUCTURE` | *"Structures of proteins **nobody has solved** appear on nobody's schedule."* | grep for a PDB/deposition census | none found. **UNVERIFIABLE** |
| `modalities.json` `MOD-RET` (2nd clause) | *"a molecular state this disease **is not reported to be in**"* | as clause 5 | the grading weakens the ligand-activation route but does not census what has been *reported*. **UNVERIFIABLE** |
| `MOD-WNT-BETA-CATENIN` | *"…but that leaves the question **unrun** rather than answered"* | `grep` chondrosarcoma comparison | the clause names its own remedy (*"62 chondrosarcoma GSE series exist in GEO"*); no such comparison in the corpus. **UNVERIFIABLE**, and near-self-scoped already |
| `MOD-AROMATASE` | *"a receptor EMC **has not been shown to depend on**"* | `grep -rn "aromatase" research/modalities/*.json research/literature/*.json` | hits are repurposing-shard MoA labels only; the expression grading does not cover `ESR1`/`CYP19A1`, and a *dependency* claim needs functional data that DepMap has no EMC line for. **UNVERIFIABLE** |
| `plan.json` block 41 | *"**That benchmark does not exist yet**"* | `grep` benchmark set | `protfep_refcheck.py:188` and `tests/test_protfep_wedge_scan.py:6` confirm the existing set *"BRACKETS the wedge without covering it"* — consistent with the clause, not a refutation. **UNVERIFIABLE** |
| `requirements.json` `R6.claim_ceiling` + `.claim_ceiling_raw` (**2**) | *"a term **nobody has computed**"* | grep for an opening-penalty computation | none. `instrument-options.json` IC-4 `does_not_license` explicitly forbids reporting a detection fraction as `dG_open`. **UNVERIFIABLE** |
| `strategies.json` `ST-OCCUPANCY.limitations[0]` | *"**has never been tested by anyone**"* | as `BLK-FUNCTIONAL-ACTIONABILITY` | same wet-lab question. **UNVERIFIABLE** |
| `ST-CARE-DELIVERY.thesis` | *"**no systemic agent has a demonstrated survival benefit**"* | `grep -rn "survival benefit" research/modalities/*.json` | **zero hits.** No committed trial census either way. **UNVERIFIABLE** |
| `technologies.json` `TECH-JUNCTION-PMHC.why_it_matters` | *"all three routes rest on the same **unmeasured** premise"* | grep junction presentation | no measurement of junction pHLA presentation in the corpus. **UNVERIFIABLE** |

### R.5 — ⭐ Incidental refutation found inside a graded field, reported because it is stronger than the clause `PRIMARY`

`technologies.json` `TECH-RECONSTRUCTED-IPD.evidence[1]` opens: *"⛔ **THE ARM THAT HAS NOT LANDED IS THE DATA. No published EMC figure has been digitized into it, so the artifact computes over an empty CURVES table** and says so."* Its `not_scannable_because` repeats it: *"`curves_supplied` in research/modalities/emc-ipd-survival.json, **which is 0 today**"*.

`research/modalities/emc-ipd-survival.json` — **in the corpus and in the live checkout, both showing the same value** — states:

> `curves_supplied: 1`, `curves_hand_typed: 0`, `curves_from_digitizer: 1`, `curves_admissible: 1`, `curves_pooled: 1`, `status: "curves supplied; see quality[] for what was admitted and why"`, with one reconstruction `stacchiotti2013_pfs_anthracycline::risk_table_anchored` (`n_reconstructed: 11`, `max_abs_km_deviation: 0.0454`, `admissible: true`).

⭐ **A figure has been digitized, the CURVES table is not empty, and the watcher number is 1 rather than 0.** Both sentences are false against the artifact each one names. This sits in W26b's OVER-SCOPED field (`not_scannable_because`) and in one of its UNVERIFIABLE fields (`evidence[1]`), so it is not a re-grade of either clause — it is a different, harder defect in the same two fields, and it is the kind that a stale watcher number hides indefinitely.

**Smallest correct restatement**, `systems/graph/technologies.json`, `TECH-RECONSTRUCTED-IPD.evidence[1]` (the field's first two sentences; the live file is one JSON line per record, so quote by record id rather than by line number — my `evidence[1]` read is at the record `TECH-RECONSTRUCTED-IPD`): *"⭐ **THE ARM HAS BEGUN TO LAND: one curve is digitized and admissible** (`emc-ipd-survival.json`: `curves_supplied 1`, `curves_from_digitizer 1`, `stacchiotti2013_pfs_anthracycline::risk_table_anchored`, n = 11, max |ΔKM| 0.0454). Whether the capability reaches useful power depends on how many EMC series print a numbers-at-risk table — **counted for 5 of 17 candidate series as of 2026-08-27: 2 print one, 3 do not**."* And in `not_scannable_because`, replace *"which is 0 today"* with *"which is 1 today"*.

⛔ No clinical claim: every figure above is a count of what a published series *reported* or a transcript contrast in archival tissue, carried here only to check a sentence in a JSON file. Nothing bears on whether any treatment works.

---

## Validation evidence

Environment: Linux, Python 3.11 stdlib, no network, no paid API, no GPU. Read-only Bash on `/home/user/Rare-cancers` and on `/tmp/claude-0/frozen-corpus/extracted/corpus`.

### `RUN` — corpus root and scale
```
$ find /tmp/claude-0/frozen-corpus/extracted/corpus/ -type f | wc -l
5996
$ cd .../corpus && for d in */; do echo -n "$d "; find "$d" -type f | wc -l; done
research/ 5577   scripts/ 67   systems/ 173
```

### `RUN` — corpus-only surface (the novelty of this lane)
```
$ find . -type f | sed 's|^\./||' | sort > corpus-files.txt   # 5996
$ while read f; do [ -e "/home/user/Rare-cancers/$f" ] || echo "$f"; done < corpus-files.txt | wc -l
2201
```

### `RUN` — the artifact carrying 8 of 11 refutations
```
$ python3 -c "... json.load('research/modalities/census-route-expression-grading.json') ..."
ROUTES: ['RT-ARGININE','RT-RET','RT-HYPOXIA-PRODRUG','RT-MATRIX-SYNTHESIS','RT-ALK-HIT',
 'RT-MATRIX-ADDRESS','RT-IMMUNOCYTOKINE','RT-NR2F1','RT-MTAP-PRMT5','RT-TXN-CDK','RT-CHAPERONE',
 'RT-APOPTOSIS-DEP','RT-MDM2','RT-EZH2','RT-SGK1','RT-POLQ']
platforms: GPL6244 (6 EMC vs 29 comparator sarcomas); GPL3290 (10 EMC vs 6 comparator)
```

### `RUN` — SSTR2 measurement, two independent reads
```
emc-tissue-read-statistics.json  primary.GPL6244.SSTR2:
  delta -0.0424  t -0.397  df 5.3  p 0.707208  ci -0.3127..0.2279  n_emc 6  n_comparator 29  significant false
gse28866-tumour-vs-normal.json   SSTR2: emc_median 0.35226  normal_median 0.22813  sarcoma_median 0.25671  _n_emc_libs 4
                                 SSTR2: emc_over_normal 1.5441 (pct 89.2)  emc_over_sarcoma 1.3722 (pct 84.0)
```

### `RUN` — write isolation and cleanup
```
$ git status --porcelain | wc -l          # start 0, end 0
$ find /tmp/claude-0/frozen-corpus/extracted/corpus -newermt "2026-09-08 02:35" -type f | wc -l
0
$ rm -rf /tmp/claude-0/w26c && ls -d /tmp/claude-0/w26c
REMOVED /tmp/claude-0/w26c
ls: cannot access '/tmp/claude-0/w26c': No such file or directory
```

### `PROPOSED (NOT RUN)`
- Landing any of the 11 + 3 + 1 restatements. **Nothing applied**, per my dispatch and the brief's write isolation.
- Regenerating views and measuring the blast radius of these clauses. Not run; W26b's radii cover only its own 16 fields and do not transfer to mine.
- `scripts/preflight.sh` in any form. Not run; not authorised.

---

## Limitations

- **My 16 UNVERIFIABLE rows are search outcomes, not absences.** For each I state the pattern searched and the root. `metadata/snapshot-provenance.json` records `"is_complete_repository": false` and `"absent_files": "Unknown/unprovided"`, so nothing missing from the snapshot is missing from the repository, let alone from the literature.
- **Recall of my searches is unmeasured.** I searched named genes, named documents and named counts. A refutation phrased in terms I did not guess is invisible to me, so **11 FALSE is a floor, not a census** — the same error this lane exists to name.
- **10 of my 11 refuting files are present in the live checkout too.** The corpus is what made me look, but the coordinator should not read these as corpus-only discoveries; the honest statement is that W26b's live-tree sweep did not open them. The one strictly corpus-only corroboration is `research/autonomy/nr4a3-program-tissue-2026-09-07/analysis-config.json` (`previously_exposed_gene_exclusion` naming SSTR2), which is supporting, not load-bearing.
- **Transcript is not copy number, protein, or activity**, as `census-route-expression-grading.json`'s own `_language_discipline` states. My clause-2 and clause-5 verdicts turn on that distinction and are worded to preserve it.
- **The two-platform EMC reads are small (n = 6 and n = 10 EMC)**, and the file itself warns that magnitudes are not comparable across platforms — only sign agreement is. My verdicts rest on `readable: true` and on the existence of a graded verdict, not on any effect size.
- **I did not re-grade W26b's 16 defective clauses and did not verify its blast radii.** Where my evidence bears on one of them (`ST-OCCUPANCY.limitations[1]`, which W26b called OVER-SCOPED and whose twin `MOD-TF-LBD-OCCUPANCY` I call FALSE), I say so and leave its grade alone.
- **The clause count is 30, not 29**, because W26b listed `BLK-FUNCTIONAL-ACTIONABILITY.statement_about` in two classes. Both readings are preserved above.
- No clinical claim, no efficacy claim, no wet lab.

---

## Stop condition

**Set up front:** return the moment (a) each of W26b's UNVERIFIABLE clauses has been recovered verbatim from the live graph, (b) each has had at least one targeted corpus search run against its concrete proposition, (c) every verdict change carries a quoted evidence path resolving under `corpus/`, and (d) every non-change is reported as a search rather than an absence — or at ~40 tool calls / ~40 minutes, whichever came first.

**MET, inside budget, on all four legs.** 30/30 clauses recovered and searched; 14 verdict changes, each with a quoted path; 16 non-changes each reported as the search that produced them; one incidental refutation disclosed rather than folded into a clause grade. Nothing applied, nothing written, scratch deleted.

---

## Tool-call and wall-clock count actually used

**19 tool calls.** **Wall clock ≈ 10 minutes** (~03:38Z first call, `date -u` end `03:47:52Z`; the recorded start `03:43:06Z` is when the corrected constraint block arrived, not my first call). Both well inside the ~40/~40 target. The saving comes from W26b's report supplying the clause list, so no enumeration instrument had to be built.

---

## Next concrete action

**Land the two `strategies.json` refutations first — `ST-RADIOLIGAND.limitations[0]` and `ST-REPURPOSING.limitations[1]` — because `strategies.json` is the one file W26b measured as fanning out to 5–8 view pages per `limitations[n]`, so a false absence there is reprinted on every route page in the family as if independently confirmed.** Both are one-clause edits in one file, both are refuted by a file already committed in the live tree (`emc-tissue-read-statistics.json`, `census-route-expression-grading.json`), and the corrected wording for `ST-RADIOLIGAND` is a *stronger* scientific statement than the one it replaces: a measured null instead of an unmeasured gap.

**One thing the lander must be told, because a diff will not show it:** `TECH-RECONSTRUCTED-IPD` (R.5) says its own watcher number is 0 when the artifact says 1. That is a stale-watcher defect, not a prose defect — fixing the sentence without re-reading `emc-ipd-survival.json` at land time will simply re-freeze whatever number is stale then. It needs a reader, not a gate.
