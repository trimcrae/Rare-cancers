<!-- collected 2026-09-08T07:20:55Z by campaign coordinator; agent id ab2376c8974b3232b; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ab2376c8974b3232b.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**A3**, cross-paper strategy-layer scouting stream, campaign OPUS-CAPACITY-CAMPAIGN-20260908.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

**Start** `date -u` = `Tue Sep  8 07:11:04 UTC 2026` · `git rev-parse HEAD` = `666b1fd2a6d324233291c24ec1429f24609954b1` · `git status --porcelain` = empty · `df -h /` = 252G total, 20G avail (47%).
**End** `date -u` = `Tue Sep  8 07:17:15 UTC 2026` · `git rev-parse HEAD` = `2e803291d58c4a5a8fc3be0dce4e4a4a721e74e9` · `git status --porcelain` = empty (a transient `wc -l` of 2 was observed at 07:17:15 and was gone one call later — a coordinator commit landing mid-read, not a write by me; I made **no repository write**) · `df -h /` = 20G avail. HEAD advanced under me, as COMMON-BRIEF §1 says to expect.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,...
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy config)
NO_PROXY=localhost,127.0.0.1,::1,... 
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

The end-of-run grep returned the identical set (spot-checked on `CLAUDE_CODE_VERSION=2.1.42`, `AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_EFFORT=medium`, `ANTHROPIC_BASE_URL=https://api.anthropic.com`, `CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6`).

## Stream and question

The layer above routes: all 14 rows of `systems/graph/strategies.json` and all 21 of `systems/graph/blockers.json`.

**Question pursued:** which strategy's own recorded `next` is (i) still unmet, (ii) supported by inputs actually committed and reachable, and (iii) a substantively separate paper question — ranked, ending in one recommended next executable checkpoint.

**Answer, up front: none of the 14 qualifies.** Eight `next` fields are **STALE** — recorded open, answered by committed artifacts. Four are unmet and unreachable (wet lab / live authorization / future technology). One is closed by its own record. One (`ST-REPURPOSING`) is a standing watch whose awaited input **arrived, was fetched, quantified and committed** — and, measured against the promise in the `next` field itself, **cannot do what the field says it would**. That last row is the finding I rank first, and it is a scientific finding about the strategy layer, not a paper.

## Prior-work and exclusion check

Read in full first: `CLOSED-WORK.md` (70 lines), `CORPUS-CONTEXT.md` (82), `paper-lane/DECISION-synthetic-line-and-S6.md` (279), and `COMMON-BRIEF.md` (1,029; §1–§5, the measured-results block, and the whole 05:10Z→end paper-lane section including the P2 correction and results P1–P4). Searches run over the live tree: `git ls-files | grep -i -E "matrix|microenv|myxoid|stroma"`, `grep -rl -i "glycosaminoglycan"`, `grep -rn "GSE243553"`, `grep -rl -i "terminal.event"` — each with `research/autonomy/opus-capacity-campaign-20260908` filtered out where it produced sibling-report noise (COMMON-BRIEF §3: a sibling's report is not prior art).

Confirmed not replayed: P1–P6 and their dispositions; S1/S3; the NR4A Perspective and P6's proposed manuscript; the W25 / GSE243553 / primary-article / Results / novelty hold; every CLOSED-WORK denied source (Pazopanib, Sunitinib 2014, Wagner PMID 32856598, CTARC, Trabectedin/RT, Hofvander, Brenca); GSE4303/GSE28866 (read only as the *platform label* on already-committed panel scores — no re-reading of the deposits, no rediscovery claimed); PMID 22592656; the parked synthetic figure-validation family (no sweep, no point-count successor, no figure-validation route proposed). No network call was made. No `scripts/preflight.sh`. `research/modalities/atr_hrd_sarcoma_series.py` was never invoked.

**On the coordinator's NR4A correction:** no strategy here is excluded because "NR4A" appears in it. `ST-PROXIMITY` and `ST-OCCUPANCY` are the two NR4A3-centred families and both were adjudicated on their own recorded evidence with the specific hold cited — see the table and the authorization inspection. The only NR4A-specific holds I cite are the two you name, and I propose neither.

## Strategy-by-strategy next-step status

| # | Strategy | Its `next` (abridged) | Met? | Committed evidence I checked |
|---|---|---|---|---|
| 1 | `ST-PROXIMITY` | Run the binary paralogue-selectivity control (built, staged, unrun) | **UNMET, UNREACHABLE** | `BLK-SELECTIVITY-CONTROL-UNAUTHORIZED`: *"The decision was TAKEN on 2026-09-02 and it was NO."* Live enforcer read below. Recorded correct next action: **NONE** |
| 2 | `ST-OCCUPANCY` | State the selectivity requirement — "currently unsized" | **MET → STALE** | `BLK-UNSIZED-REQUIREMENT.kind_history`: absent-specification half **retired 2026-08-07**; `selectivity-requirement-sizing.md` states it for RT-MONOVALENT / RT-TCIP / RT-ASYMMETRIC as nine rows with quantity, comparator and asymmetry-correct pair form. Strategy `last_verified` = 2026-08-05, i.e. *before the answer existed* |
| 3 | `ST-FUSION-DIRECT` | "Nothing." | **N/A** | `work_state: dead`, `status: closed`, `confidence: high` |
| 4 | `ST-NUCLEIC-ACID` | Keep the arc publishable; **watch** for delivery tech / an EMC-enriched surface antigen | **MET (writing) / UNREACHABLE (watch)** | `PUB-ASO` = `posted_preprint`. `BLK-DELIVERY` and `BLK-VECTOR-DELIVERY` are both `requires_future_technology` |
| 5 | `ST-IMMUNO` | Regenerate junction-neoantigen predictions against the corrected exon index | **MET → STALE** | `research/modalities/fusion-neoantigen-retraction.json`, `_utc 2026-08-07T00:57:09Z`, *"CLEARED — regenerated on the corrected transcript model and it re-derives"*, 8/8 checks `ok`, corrected denominator 5 junctions / 11 predicted binders / 4 strong. `PUB-NEOANTIGEN`, `PUB-HLA-COVERAGE`, `PUB-VACCINE-PATH` all `drafted` |
| 6 | `ST-REPURPOSING` | **Watch for a fetchable public EMC expression dataset** — "the single input that would convert most of this family from class-inherited argument to measurement" | **STALE — and the promise fails on arrival** | See ranked item 1 below |
| 7 | `ST-RADIOLIGAND` | Keep on the ask list; a negative scan kills it cheaply | **UNMET, UNREACHABLE** | `BLK-NO-WET-LAB` = `requires_external_collaboration`. A scan is a clinical act; there is no wet lab |
| 8 | `ST-DEPENDENCY` | Keep the computed vulnerability assessment as a standalone deliverable | **MET → STALE** | `PUB-ATR` `drafted` (`emc-atr-vulnerability-assessment.md`); `PUB-ATR-PANEL-ASK`, `PUB-SYNLETH`, `PUB-BIOMARKER-DEP`, `PUB-TXN-DEPENDENCY` all `drafted` |
| 9 | `ST-DISSEMINATION` | "Nothing blocks it. Write it." | **MET → STALE** | `PUB-METHODS`, `PUB-CLOSED-ROUTES`, `PUB-MODALITY-CENSUS` all `drafted` with committed documents |
| 10 | `ST-MICROENV` | Grade the GAG and sulfate-donor read "already committed here and never read for this purpose" | **MET → STALE** | `emc-expression-panels.json → panels.cs_gag_paps / reads.read_2_CS_GAG_PAPS` already carries per-group, per-platform scores **and verdicts**; `census-route-expression-grading.json → routes.RT-MATRIX-SYNTHESIS / RT-MATRIX-ADDRESS` carry the grades; P5 wrote it up in full |
| 11 | `ST-LOCOREGIONAL` | Extract primary site / metastatic site / burden; size the eligible fraction | **MET IN PART → STALE on site** | `emc-site-curation.json` resolved primary site 2026-08-25/27; `emc_locoregional_eligibility.py:52-56` marks the old "not curated" sentence *"Superseded, retained"*. P3 reproduced both pools. Burden confirmed absent everywhere; RT-LUNG-DIRECTED numerator not extractable |
| 12 | `ST-STRATEGY` | Pool the curated cohorts' PFS data | **MET → STALE, and the pool is policy-refused** | `emc-scheduling-medians.json` (generator `emc_scheduling_medians.py`, ledger AUT-060, route RT-SCHEDULING) carries the four medians and states *"no quantity here combines two arms"* + `analyses.A7_the_pool_that_is_refused`, under POLICY-evidence §2.4. `PUB-STRATEGY-ARCH`, `PUB-ENDPOINT` `drafted` |
| 13 | `ST-CARE-DELIVERY` | Digitize the KM curves and run `emc_ipd_survival.py` | **MET → STALE** | `km-figure-readings.json`, `km-swimmer-readings.json`, `km-risk-row-detection.json`, `emc-ipd-survival.json` all committed; P1 verified `--check` exits 0, 7 curves, 11 patients / 9 events, 4 swimmer, 2 table |
| 14 | `ST-MORTALITY-MECHANISM` | Read the terminal-event corpus and classify each quoted sentence | **MET → STALE** | `emc-terminal-events-classified.json` + `emc_terminal_events.py` committed; `PUB-MORTALITY-MECHANISM` = `drafted` (`emc-mortality-mechanisms-paper.md`). It is the only strategy with `blocked_on: []` — and it is already written |

**Systematic staleness, measured:** 9 rows carry `last_verified: 2026-08-05`, 5 carry `2026-08-09`. Every artifact that answers a `next` is dated **2026-08-07 or later**, and P1/P3/P5's 2026-09-08 work answers three more. The strategy layer has not been re-read in a month. *That, on its own, is a bookkeeping observation and not a paper* — which is why it is not my decision.

## Blockers that gate the shortlist, by kind and owner

| Blocker | `kind` | `owner` | What it actually gates, and whether it is a measurement gap |
|---|---|---|---|
| `BLK-SELECTIVITY-CONTROL-UNAUTHORIZED` | **requires_authorization** | `research/manuscripts/nr4a3-program-map.md#31--the-instrument-table`; the retiring act is **trimcrae's alone** | Gates `ST-PROXIMITY`'s `next`. **Not a missing measurement** — the instrument is built, staged and priced. A standing human NO |
| `BLK-NO-EMC-DATA` | insufficient_data | `research/IDEAS.md` | Gates 7 strategies nominally. Its own `retired_by_action` names the fourth cohort — see item 1: the dataset arrived, so the *nominal* gap is not what still blocks |
| `BLK-NO-CURATED-CLINICAL-DATA` | insufficient_data | `systems/graph/blockers.json` | Gates `ST-CARE-DELIVERY`. Its own text separates the halves: **three of six fields are absent from the reachable publications** — a reporting gap in the world, not an un-taken extraction |
| `BLK-NO-WET-LAB` | requires_external_collaboration | `research/manuscripts/modality-census/what-a-civilian-can-buy.md` | Gates `ST-RADIOLIGAND`, `ST-DEPENDENCY`. A capability that does not exist here |
| `BLK-UNSIZED-REQUIREMENT` | requires_wet_lab (was `scientific_uncertainty`; changed 2026-08-07) | `selectivity-requirement-sizing.md` | Gates `ST-OCCUPANCY`. Residual = three unmeasured dose-responses (MISSING-1/2/4). **Explicitly not retirable by any computation** |
| `BLK-DELIVERY`, `BLK-VECTOR-DELIVERY` | requires_future_technology | ASO working record; `emc-post-degrader-options.md` | Gate `ST-NUCLEIC-ACID`. Capabilities the world does not have |
| `BLK-ANTIGEN-COLD` | fundamental_biological_limit | `immunotherapy-options-emc.md` | Gates `ST-IMMUNO`. Not retirable by data |
| `BLK-REGISTRY-DUA` | **requires_authorization** | `systems/graph/blockers.json`; retiring act trimcrae's alone | Gates `PUB-EMC-CLASSIFICATION` (`drafted`), a paper CLOSED-WORK records the **user rejected**. Not live in either direction |

**Authorization-boundary inspection (coordinator correction 2), read-only, no gate touched or tested.** `BLK-SELECTIVITY-CONTROL-UNAUTHORIZED` is **not a stale record**: its stated reason matches the live enforcer exactly. `research/autonomy/autonomy-state.json → gpu_spend_prohibited` reads `active: True`, `set_utc: 2026-09-02T16:35:00Z`, `set_by: "trimcrae, 2026-09-02, in session"`, `scope: "every GPU rental, fleet, fan-out and dispatch made by this automation, at any price, including $0 free-credit lanes and including a resume of a previously started run"`. `research/autonomy/gpu_ban.py` is the enforcement half and fails closed on a missing file, an unparseable file, a missing block, or a non-boolean `active`; `active: false` read from a real file is the only permitting state. The row also records that the last cycle to re-derive the price against CLAUDE.md §2's ≲$50 ceiling reached a buy decision that trimcrae interrupted at $0 spent. **The missing condition is a human authorization that was asked and answered NO. I name it and stop.** `BLK-REGISTRY-DUA` is likewise current, and carries its own prior-question warning (two published SEER studies read ICD-O-3 9231/3 as two mutually incompatible diseases), so buying access first buys a contaminated denominator.

## Ranking and criterion

**Criterion — paper merit, stated before tractability was consulted:** *would a reader outside this program change what they do because of the answer, and can that answer be checked line-for-line against committed evidence?* Cost, runnability and convenience were deliberately not inputs; the S6 decision's own rule applies — runnability is not a reason to run.

Per the coordinator's correction 1, **distinct ≠ eligible**. Three separate tests were applied to each shortlisted row and are reported separately: **(A) genuinely separate question**, **(B) required input actually reachable**, **(C) non-overlap with `drafted`/`posted` endpoints, CLOSED-WORK and the P1–P6 lanes**.

| Rank | Row | A separate? | B reachable? | C non-overlapping? | Verdict |
|---|---|---|---|---|---|
| 1 | `ST-REPURPOSING` | **yes** | **partly — and that is the finding** | **yes** | Highest merit; **not a paper**. See DECISION |
| 2 | `ST-PROXIMITY` | yes | **no** — live authorization NO | yes | Missing condition named; stop |
| 3 | `ST-OCCUPANCY` | no — answered 2026-08-07 | residual needs a bench | yes | Stale field; residual is wet lab |
| 4 | `ST-MICROENV` | no — graded, and P5 wrote it | n/a | **no** — P5 lane | Excluded |
| 5 | `ST-LOCOREGIONAL` | no — P3 | numerator not extractable | **no** — P3 lane | Excluded |
| 6 | `ST-CARE-DELIVERY` | no — P1 | n/a | **no** — P1 lane | Excluded |
| 7–14 | the rest | no | — | mostly inside `drafted` endpoints | Excluded |

## DECISION: recommended next checkpoint

**Ranked #1 is `ST-REPURPOSING`, as a STALE `next` field, and the live unmet question is stated below rather than the staleness itself. The recommended checkpoint is a bounded evidence adjudication, and it is explicitly NOT a paper admission.**

**(a) The unmet question, and why it matters.** `ST-REPURPOSING.next` says: *"Watch for a fetchable public EMC expression dataset — it is the single input that would convert most of this family from class-inherited argument to measurement."* The dataset **arrived**. `BLK-NO-EMC-DATA.retired_by_action` names PRJNA1357027 / SRP640302 — a real, public, fourth EMC cohort, n = 12 FFPE tumours, downloadable since 2025-11-11 — and it is no longer merely findable: `research/modalities/emc-fourth-cohort-quant.json` holds a **committed gene table** (`gene_counts_sha256 = 8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc`, byte-identical to the recomputed digest; 862 genes with ≥1 assigned probe; 1,645 probes offered, 906 assigned, **662 unassigned**), plus per-run EWSR1 break-apart FISH (8 positive / 4 negative) and the depositors' 6-good / 6-poor prognosis split. **And the same artifact refuses the very thing the strategy was waiting for:** *"⛔ NO DIFFERENTIAL-EXPRESSION RESULT IS COMPUTED OR REPORTED FROM THIS COHORT, AND THAT IS THE FINDING RATHER THAN A GAP"* — six versus six, five d.f. per arm, one sequencing batch, FFPE spanning 1997–2020, no adjustable covariate; *"a ranked gene list from that design would be dominated by which of the twelve specimens degraded least."* **So the live unmet question is not "has a dataset arrived" but: can any committed EMC dataset support a per-agent, expression-based repurposing claim at all, or is this family permanently class-inherited?** From committed evidence the answer already leans **no**: the two array series carry a measured, gene-set-independent arm-to-arm offset whose cause is UNKNOWN (W02k: E1 fires for 0.2950 of random 14-gene panels, E2 for 0.2075 — 4.15× nominal), and the fourth cohort refuses DE by design. It matters because 10 of this family's 11 routes have **never** been read against the fourth cohort — `emc-fourth-cohort-route-readout.json` adjudicates 16 routes and only `RT-TRABECTEDIN` of them — so the graph currently records a family "waiting for data" that has in fact received its data and been answered.

**(b) Exact reachable inputs and access limits.** Committed, $0, no network: `research/modalities/emc-fourth-cohort-quant.json` and its gene table (digest above); `research/modalities/emc-fourth-cohort-route-readout.json` and its generator `emc_fourth_cohort_route_readout.py`; `systems/graph/routes.json` (the 11 `ST-REPURPOSING` routes and their `required_validation` lists); `systems/graph/blockers.json`. **Access limits, stated:** 662 of 1,645 probes are unassigned to any gene — the vendor probe manifest with per-probe transcript targets **is not on disk** and fetching it is a network act outside this container; an unassigned probe is `⛔ NOT a reading of absence`. No differential expression is available at this n and design and none may be computed. The two array series are **out of bounds for any new panel statistic** — COMMON-BRIEF: *"Do not dispatch further lane-2 statistics on `emc-expression-panels.json`. No new lane-2 worker."*

**(c) Proposed contribution and novelty uncertainty.** The contribution is a **corrected strategy-layer status**: the awaited input arrived and does not perform the conversion the `next` field promised, with the exact per-route reason. **Novelty uncertainty: HIGH, and I do not claim this is a paper.** The adjudication *pattern* already exists in the repository (`emc_fourth_cohort_route_readout.py`); what is new is only its extension to 10 routes it never covered. Whether even a complete negative here has publishable merit is **UNKNOWN** and would need its own separate decision on its own evidence — exactly the standard the S6 narrowing sets (*source availability is not paper admission; a null is a bounded reachability statement*).

**(d) Distinction from prior no-gos.** Not the synthetic figure-validation family (no digitization, no reconstruction, no figure). Not S6 (no source hunt, no PubMed, no network). Not P4/`PUB-KINASE-LEADS` — P4 graded four *named leads* against arrays and UniProt; this reads *route-level required_validation gene lists* against a **different deposit** P4 never used. Not P5/`PUB-MATRIX-ADDRESS` (different strategy, different routes, different artifact). Not lane 2 — **no panel statistic, no arm comparison, no t-test, no score**: a readability adjudication computes nothing across arms. Not a record or consumer census and not an infrastructure audit: the object graded is scientific readability of a gene in a committed expression table, not a field's consumers. Not GSE4303/GSE28866 and not GSE243553.

**(e) Finite acceptance for the next checkpoint.** For each of the 10 `ST-REPURPOSING` routes not covered by the existing readout, one row per `required_validation` gene, graded **READABLE** (≥1 assigned probe in the 862-gene space), **UNDECIDABLE** (matched only by an unassigned probe), or **UNREAD** (off-panel), every row traceable to gene-table digest `8aa3064a…`; plus a one-line per-route disposition; plus a banner stamped on every row that a READABLE verdict is an **instrument state and never a repurposing measurement**, because DE is refused at this design. A route whose `required_validation` list is absent is recorded as such, not inferred.

**(f) Stop condition.** Stop when the 10 routes are adjudicated, or when a route's `required_validation` list proves absent, or at ~40 tool calls / ~40 minutes — whichever first. **Hard stops:** stop immediately if the work would require any cross-arm statistic (that is lane 2, closed), any network fetch (the probe manifest), or any DE computation. Writing the result into `systems/graph/` is an **owner act**, not a worker act — the checkpoint produces a report, not a graph edit.

## Rejected and why

- **`ST-PROXIMITY`** — rejected on **B (reachability)**, not on merit. Live `active: True` category ban set by trimcrae 2026-09-02, enforced fail-closed by `gpu_ban.py`. The blocker's own text warns that re-deriving the price *"has rediscovered the 2026-09-02 mistake rather than found new work."* I take no action on it.
- **`ST-OCCUPANCY`, `ST-IMMUNO`, `ST-STRATEGY`, `ST-DEPENDENCY`, `ST-DISSEMINATION`, `ST-MORTALITY-MECHANISM`, `ST-MICROENV`** — rejected on **A**: the `next` is answered by a committed artifact, and in five cases sits inside a `drafted` endpoint. A stale field plus a new title is not a distinct paper.
- **`ST-CARE-DELIVERY`, `ST-LOCOREGIONAL`, `ST-MICROENV`** — additionally rejected on **C**: P1, P3 and P5 own them this campaign.
- **`ST-NUCLEIC-ACID`, `ST-RADIOLIGAND`** — rejected on **B**: future technology and an external wet-lab collaborator.
- **`ST-FUSION-DIRECT`** — closed on facts about the objects by its own record.
- **The tempting cross-cut I did NOT recommend, recorded so it is not lost:** P5's matrix paper's *only concordant cross-platform negative* is the PAPS sulfate-donor module (−0.3096 SD, t = −2.234; −0.1616 SD, t = −2.113), and it is exactly the kind of arm-to-arm panel verdict that W02k measured to fire at ~4× nominal on random panels from the same substrate, with a directional gene-set-independent offset of **UNKNOWN** cause. Placing that module against W02k's null would be informative — **and it is forbidden**: it is further lane-2 statistics on `emc-expression-panels.json`, lane 2 is closed, and its own named reopening input (the uncommitted GSE24369 series matrix) is **DENIED**. I recorded it and stopped. Nothing here withdraws or weakens P5's finding; I ran no statistic.

## Durable artifacts written and verified

`/tmp/claude-0/a3-retained/` — **not deleted**, parent alone collects:

| file | bytes | sha256 |
|---|---:|---|
| `strategy-next-adjudication.json` | 10,330 | `02fc3b6b4376f94d511b0515194952cd14680af02baf4688b1ddf2ee92ae957f` |
| `authorization-boundary-inspection.md` | 3,604 | `c0d21d2896a9d084818f80d42784c7f9ee9fe918e2194f6136361ca570bd77cd` |
| `SHA256SUMS` | 201 | (manifest) |

`sha256sum -c SHA256SUMS` → **2 of 2 OK**, run in place at 07:17. `python3 -c "json.load(...)"` on the JSON → `JSON OK`. Free disk 20 GiB at both ends, ≥10 GiB floor honoured throughout.

## Validation evidence

**RUN:** `date -u`, `git rev-parse HEAD`, `git status --porcelain`, `df -h /`, `env | grep …` (start and end, both exit 0); `wc -l` over the four mandated documents; `python3` reads of `strategies.json` (14 records), `blockers.json` (21), `publications.json` (33), `emc-expression-panels.json`, `emc-fourth-cohort-route-readout.json`, `emc-fourth-cohort-quant.json`, `fusion-neoantigen-retraction.json`, `emc-scheduling-medians.json`, `routes.json`, `autonomy-state.json` — all exit 0; `sed -n` reads of `gpu_ban.py:1-40` and the P5 report; four `grep`/`git ls-files` prior-work searches; `sha256sum` + `sha256sum -c` (2/2 OK); `json.load` parse check.
One command returned **exit 128**, reported verbatim rather than smoothed: `git rev-parse HEAD` executed with the shell's cwd inside `/tmp/claude-0/a3-retained` → `fatal: not a git repository (or any of the parent directories): .git`. Re-run from the repository at 07:17:15 it returned `2e803291d58c4a5a8fc3be0dce4e4a4a721e74e9`. The hash verification in that same command **did** complete (2/2 OK) before the failing step.
**PROPOSED (NOT RUN):** the entire recommended checkpoint. No route adjudication was executed; no gene was graded against the fourth cohort by me.
**NOT RUN, deliberately:** `scripts/preflight.sh`; `atr_hrd_sarcoma_series.py`; any network call; any statistic on `emc-expression-panels.json`; any repository write.

## Limitations

Verdicts rest on reading committed artifacts and their own self-descriptions — I executed none of the generators, so every "MET" is *an artifact exists that answers the field*, not *I reproduced its numbers*. `emc_fourth_cohort_route_readout.py` was read through its output artifact only; I did not confirm by execution that no `ST-REPURPOSING` route beyond `RT-TRABECTEDIN` appears anywhere in its logic. Route→strategy attribution came from a `parent`/`strategy` key match in `routes.json` and may under-count routes that record the relation differently. I read the **live checkout**, not the frozen corpus; per CORPUS-CONTEXT that is the correct tree for `systems/graph/publications.json`, which is one of the three files whose line numbers shift between trees. Absence of a covering artifact is **UNKNOWN, not proof of absence**. Nothing here is a paper admission, a manuscript, a publication act, or a graph edit. No clinical efficacy, safety, selectivity, therapeutic-window or readiness claim is made or implied by any row; there is no wet lab. No patient data, citation, measurement or completion record was invented, and no negative was softened — P5's matrix findings, W02k's two withdrawals, and the S6 zero-matched-pairs result all stand exactly as recorded.

## Stop condition

Set: *stop at a delivered ranked decision, or ~40 tool calls / ~40 minutes.* **Met** — the ranked decision is delivered, well inside both bounds. Not blocked.

## Tool-call and wall-clock count actually used

**25 tool calls** (all Bash; 1 returned exit 128, reported above). **Wall clock 07:11:04 → 07:18 UTC ≈ 7 minutes.** No repository write, no network, no git write operation, no subagent.
