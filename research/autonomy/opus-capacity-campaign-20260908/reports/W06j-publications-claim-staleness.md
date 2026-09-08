<!-- collected 2026-09-08T04:32:14Z by campaign coordinator; agent id a8bca9270d8ac4a97; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a8bca9270d8ac4a97.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Audit complete; scratch deleted; no repository writes.

## Worker

**W06j**, lane 6 (mortality-paper independence claim → `publications.json` claim-supersession), OPUS-CAPACITY-CAMPAIGN-20260908. Successor to W06i. Container checkout `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as `claude-opus-5`. Nothing I can run in this container verifies the served model; the coordinator must extract the actual per-child runtime model from the transcript.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:45:16 UTC 2026` | `Tue Sep  8 03:49:45 UTC 2026` |
| `git rev-parse HEAD` | `606d79f96526b651f3b825190d721f6b302c032e` | `063f00fa086253fb520c60a11fcf62882b3a4647` |
| `git status --porcelain` | *(empty)* | *(empty, 0 lines)* |

HEAD advanced under me. **I verified rather than assumed that nothing I measured moved:** `git diff --stat 606d79f9 HEAD -- systems/graph/publications.json systems/views/ research/manuscripts/ research/modalities/` produced **no output** — zero changed files in every path this audit reads. The coordinator commits touched only the campaign directory, consistent with the brief's W35b measurement.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start:

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 -Djavax.net.ssl.trustStorePassword=changeit -Djavax.net.ssl.trustStoreType=PKCS12 -Dhttps.proxyHost=127.0.0.1 -Dhttps.proxyPort=37223 -Dhttp.nonProxyHosts=localhost|127.0.0.1|::1|127.*|0.*|::|169.254.*|api.anthropic.com|api-staging.anthropic.com|api-pr-preview.anthropic.com|mcp-proxy.anthropic.com|mcp-proxy-staging.anthropic.com|registry.npmjs.org|jsr.io|npm.jsr.io|pypi.org|files.pythonhosted.org|index.crates.io|proxy.golang.org|host.docker.internal|10.*|172.16.*|172.17.*|172.18.*|172.19.*|172.20.*|172.21.*|172.22.*|172.23.*|172.24.*|172.25.*|172.26.*|172.27.*|172.28.*|172.29.*|172.30.*|172.31.*|192.168.*|100.64.0.0/10|*.svc.cluster.local|*.svc.cluster.local -Djdk.http.auth.tunneling.disabledSchemes= -Djdk.http.auth.proxying.disabledSchemes=
NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

Scratch `/tmp/claude-0/w06j` created and **deleted** (`rm -rf`; `ls -d` afterwards → `No such file or directory`). No repository write, no git write operation, no `--write-views`, no `preflight.sh`, no network.

---

## Question

W06i's named successor: **of the 32 `PUB-*` records other than `PUB-MORTALITY-MECHANISM`, does any `what_it_would_claim` or `outcome_potential_why` string assert content that later committed measurement in this repository has superseded — and for each one that does, which generated files carry it?**

Open because `what_it_would_claim` is rendered verbatim into the views by `systems/systems_check.py:3045` and `:3238` and is covered by **no drift check that compares it against the artifact it describes** — `[G2]` compares views against the graph, never the graph against the manuscript, the routes or the code it cites. A stale claim there is invisible to every gate and printed several times over.

---

## Prior-work check

Read in full first: `COMMON-BRIEF.md` (93 lines, including the 03:36Z/03:44Z corrections and the "Known, measured, NOT worth rediscovering" section), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `systems/POLICY-evidence.md`, and `reports/W06i-independence-sentence-consumers.md` in full (via its saved tool-result capture, all nine sections). Read the Question / Prior-work / Method heads of `W09d-views-regeneration-proof.md`, `W09e-views-blast-radius.md`, `W09f-publications-false-absence-audit.md`, `W26b-remaining-graph-files-sweep.md`, plus — found while establishing adjacency and materially relevant — the Question sections of `W09g-publications-prose-fields.md` and `W09h-successor.md`. Full `## Result` of W09f.

⚠ **Dispatch path correction, same as W09f found:** the reports live at `research/autonomy/opus-capacity-campaign-20260908/reports/`, not `reports/`. `cat reports/W06i-...` exits 1.

**Adjacency and non-overlap, stated precisely:**

| sibling | its axis | mine | overlap |
|---|---|---|---|
| W09d | does the C5 string propagate from `artifacts.json`? | — | none |
| W09e | blast radius of one field (`PUB-CARE-DELIVERY.why_not_written`) | — | none |
| **W09f** | **categorical *absence* clauses** in `what_it_would_claim` + `why_not_written` — 22 clauses, verdicts FALSE/OVER-SCOPED/UNVERIFIABLE/TRUE | **supersession by later measurement**, any clause shape, including numbers, route arithmetic and code pointers | **partial and deliberate.** Absence and supersession are different axes; W09f's R.3/R.4/R.6 happen to be supersessions. **I inherit W09f's verdicts rather than re-adjudicating them**, and contribute what W09f did not: the tree-wide numeric/route/pointer reconciliation, and the fan-out. |
| W09g | absence clauses in `outcome_potential_why`, `working_title`, `posted._evidence` | supersession in `outcome_potential_why` | same split |
| W09h | schema field *consumption* census; measured `outcome_potential_why` blast radius = 0 | I re-confirm zero by an independent 5-probe control | corroboration, not replay |
| W26b | the other 17 graph files | `publications.json` only | none |

Not replayed: `PUB-MORTALITY-MECHANISM` (W06h/W06i, excluded by dispatch); W25 (HELD — not read, not referenced); PUB-EMC-CLASSIFICATION as a route (user-rejected, closed — I audit only the wording of its graph record); the NR4A Perspective refusal; lane 11's source-index; every denied external route. **No network was used at all.** No new cohort, no source retrieval.

Campaign reports are not repository evidence: every counter-check below is a committed `file:line` I read myself.

---

## Method and inputs

Live checkout only. I did **not** read the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/` — this is a census of what the *current* tree's generator prints, and a `93b`-era snapshot answers a different question. Recorded as a limitation.

| input | role |
|---|---|
| `systems/graph/publications.json` (583 lines, **33 records**) | the source under audit |
| `systems/graph/routes.json` | route arithmetic counter-evidence (`publication.endpoint`, `publication.role`, `closure_kind`, `state`) |
| `systems/views/*.md` (the generated layer) | fan-out measurement, W06i's method |
| the 12 named `document.file` manuscripts | numeric reconciliation targets |
| `research/modalities/fusion_breakpoints.py` | the pointer PUB-NEOANTIGEN cites |
| `research/modalities/nr4a3-induced-interface-census.json`, `research/manuscripts/tcip/tcip-interface-floor-sizing.md`, `research/modalities/nr4a3-tcip-reach.json` | PUB-TCIP's three re-measurable artifacts |
| `systems/POLICY-evidence.md` | read before touching anything under `systems/` |

Python 3.11 stdlib, `git grep`, `grep`, `sed`, `git log`. **Confirmed read-only before running anything:** I executed no repository module. `systems_check.py` was read (`:3045`, `:3238` emit sites, confirming W06i's generator link) and **never executed** — no `--check`, no `--write-views`.

**Four instruments, in order:**

1. **Numeric reconciliation.** For every record with a `document.file`, extract every number ≥2 digits from both fields and test membership in the document text. Mismatches read by hand.
2. **Pointer resolution.** Regex every `path.(py|md|json|txt)[:line]` in both fields; test existence; read the cited line.
3. **Route arithmetic.** Rebuild each publication's route set from `routes.json` by `publication.endpoint` and compare counts, roles and `closure_kind` against the fields' explicit arithmetic ("two of six routes remain open", "both routes under it carry `role: context`").
4. **Fan-out**, W06i's method unchanged: grep the rendered string across `systems/views/`.

---

## Result

### R1. Honest denominator

`PRIMARY`.

| pass | n |
|---|---|
| records in `systems/graph/publications.json` | **33** |
| carrying `what_it_would_claim` | **33 / 33** (100%) |
| carrying `outcome_potential_why` | **33 / 33** (100%) |
| excluded by dispatch (`PUB-MORTALITY-MECHANISM`) | 1 |
| **records in scope** | **32** |
| **field instances graded** | **64** (32 × 2) |
| of those, adjudicated against a committed artifact I read | **25** (17 `what_it_would_claim`, 8 `outcome_potential_why`) |
| graded UNVERIFIABLE-from-the-tree | **38** |
| graded SUPERSEDED | **1** |

W09f's correction to its own dispatch is confirmed independently: 33 records, and `what_it_would_claim` is on every one of them, not 32.

### R2. `what_it_would_claim` — all 32 in-scope records

`PRIMARY` unless marked. "Inherited" = W09f's verdict on a different axis, cited and **not re-adjudicated**.

| # | record · `file:line` | claim element I could check | committed artifact checked | grade |
|---|---|---|---|---|
| 1 | PUB-ANDGATE `:11` | "names precisely what does not exist … a ligand for the EWSR1 half" | — | **UNVERIFIABLE** (W09f R.7: OVER-SCOPED vs `routes.json:3693`, inherited) |
| 2 | PUB-ASO `:23` | 8 numbers incl. "87 of 190", "61", both gapmer sequences | `aso/fusion-junction-aso-journal-article.md` — **all 8 present** | **SUPPORTED** |
| 3 | PUB-ATR `:60` | qualitative | — | UNVERIFIABLE |
| 4 | PUB-ATR-PANEL-ASK `:79` | qualitative | — | UNVERIFIABLE |
| 5 | PUB-BIOMARKER-DEP `:98` | "five therapeutic classes", "four selecting features are absent" | `dependency/emc-biomarker-selected-classes.md:9,:41,:116` — *"for four of them the state is absent"* | **SUPPORTED** |
| 6 | PUB-CARE-DELIVERY `:114` | qualitative; `document: null` | — | UNVERIFIABLE |
| 7 | PUB-CLOSED-ROUTES `:131` | "seven closed routes" implied | doc title *"Seven routes closed…"*; `routes.json` → **exactly 7** routes carry `endpoint: PUB-CLOSED-ROUTES` | **SUPPORTED** |
| 8 | PUB-DEGRADER `:146` | qualitative | — | UNVERIFIABLE |
| 9 | PUB-EMC-CLASSIFICATION `:168` | 595 / 404 / 191 / 32.1 / 37.5 / 9231 / 18 | `care-delivery/emc-icdo-9231-classification.md` — **all 7 present** | **SUPPORTED** (W09f R.6: "for the first time" OVER-SCOPED, inherited) |
| 10 | PUB-EMC-PROGRAM `:185` | qualitative | — | UNVERIFIABLE |
| 11 | PUB-ENDPOINT `:200` | 20 numbers incl. 552 / 138 / 39.4 / 20.0–54.3 / 194 / 251 / 45.5 / 2851 / 2715 / 95.2 / 31.8–73.9 / 88.9 | `endpoint/response-endpoint-indolent-tumours.md:84,:444,:654` — **all 20 present** (2851/2715 as `2,851`/`2,715`); doc `:732` records its own supersession *to* the narrow 95.2% figure the field carries | **SUPPORTED** |
| 12 | PUB-FUSION-OUTPUT `:223` | 2,276 / 39 / 88 / 11.9 / 4.2 | `fusion-output/nr4a3-fusion-transcriptional-output.md` — all present | **SUPPORTED** (W09f R.5: "No experiment has measured…" OVER-SCOPED vs `nr4a3_fusion_targets.py`'s own `⛔_how_to_state_it` rule, inherited) |
| 13 | PUB-FUSION-PARTNER `:239` | 7/15 46.7 (24.8–69.9), 6/58 10.3 (4.8–20.8), 73 patients, 78% | `fusion-partner/emc-fusion-partner-stratification.md` — all present | **SUPPORTED** |
| 14 | PUB-HLA-COVERAGE `:248` | qualitative | `routes.json` RT-VACCINE `closure_kind: premise_false` | **SUPPORTED** |
| 15 | PUB-IPD-SURVIVAL `:266` | "11 patients", "four more", "two further"; `document: null` | no committed artifact adjudicates | **UNVERIFIABLE** — but the field already carries its own dated ⚠ *Superseded, retained* marker (2026-08-25); the retention form is current |
| 16 | **PUB-KINASE-LEADS `:286`** | **"and none has been followed up by anyone, in a disease with no targeted agent"** | **`routes.json:6584` — PMID 29937513 (Urbini 2018) is the same group publishing a follow-up on the strongest lead** | ⛔ **SUPERSEDED** (W09f R.4, inherited; fan-out measured by me — R4 below) |
| 17 | PUB-LOCOREGIONAL `:300` | "a portfolio containing **no** physical intervention at all **had never** assessed any of it" | `routes.json` now carries 4 locoregional routes (RT-LIMB-PERFUSION, RT-LUNG-DIRECTED, RT-MDT-LUNG, RT-RT-INTENSIFY), all `work_state: complete`, `maturity: computed`, `last_verified` 2026-08-10 … 2026-09-02 | **SUPPORTED as written** — the past perfect scopes it to the pre-paper state; ⚠ but on a board rendered in the present tense it reads as a current absence, and four completed physical-intervention routes now exist. Flagged, not graded SUPERSEDED. (W09f graded this record's `why_not_written` FALSE, separately.) |
| 18 | PUB-MATRIX-ADDRESS `:317` | "at least three distinct handles" | 4 routes, all `parked`/`blocked` | **SUPPORTED** |
| 19 | PUB-METHODS `:337` | "the field publishes almost none of them" | world-scoped | UNVERIFIABLE (W09f R.9, inherited) |
| 20 | PUB-MODALITY-CENSUS `:352` | qualitative | — | UNVERIFIABLE |
| 21 | PUB-MONOVALENT `:370` | "never been asked by anyone" | world-scoped | UNVERIFIABLE (W09f R.9) |
| 22 | PUB-MTAP-PRMT5 `:382` | "neither has ever been examined in it" | world-scoped | UNVERIFIABLE |
| 23 | PUB-NEOANTIGEN `:404` | pointer `` `fusion_breakpoints.py:231` `` | **the pointer is stale — R3 below** | **SUPPORTED in substance; pointer defect** |
| 24 | PUB-NR-OUTSIDE-NR4A3 `:419` | "the published tool compound this program's own receptor never had" | attested repo-wide only | UNVERIFIABLE `SECONDARY` (W09f row 22) |
| 25 | PUB-PARKED-MODALITIES `:433` | "for each parked modality … a single named capability" | 5 routes, **all** `parked` **and** `instrument_limit` | **SUPPORTED** (W09f R.8 grades the `why_not_written` twin OVER-SCOPED) |
| 26 | PUB-REPURPOSING `:451` | "three independent methods", "an explicit evidence tier", "asserts no efficacy" | `repurposing/repurposing-hypotheses.md` §4.1 `:410-415` — *"Both were pre-specified, both were run, and both returned negative"* | **SUPPORTED** |
| 27 | PUB-STRATEGY-ARCH `:469` | "RT-SCHEDULING definitional, RT-SEQUENCING instrument_limit" | `routes.json` — `closure_kind` is **exactly** `definitional` and `instrument_limit` | **SUPPORTED**. ⚠ RT-SEQUENCING's `state.status` has since moved to `parked` (`last_verified` 2026-08-28); the field asserts closure *kind*, which is unchanged |
| 28 | PUB-SURFACE-TARGETS `:484` | 0.578 / 0.631 / 0.885 / 0.189 | `surface-targets/emc-surface-target-landscape.md` — all present | **SUPPORTED**; field already carries its own ⚠ SUPERSEDED 2026-08-07 RETAINED marker |
| 29 | PUB-SYNLETH `:502` | qualitative | — | UNVERIFIABLE |
| 30 | **PUB-TCIP `:520`** | **"'NR4A3' appears 0 times in `nr4a3-induced-interface-census.json` and 0 times in `tcip-interface-floor-sizing.md`; '8XTT' … 0 times in either OR in `nr4a3-tcip-reach.json`"; "names it three times"; 0.896 → 1.121 → 1.254; 6-of-15** | **I re-ran the measurement today at HEAD — R5 below** | **SUPPORTED, independently re-verified** |
| 31 | PUB-TXN-DEPENDENCY `:535` | qualitative | — | UNVERIFIABLE |
| 32 | PUB-VACCINE-PATH `:551` | "moves to zero at a **0.125**-unit change in an undefended acceptance threshold" | `neoantigen/emc-vaccine-development-path.md:343` — *"it reaches zero **0.1264** below it"* | **SUPPORTED with a MINOR DERIVED-VALUE MISMATCH** — R6 below |

**Tally (32): SUPPORTED 17 · SUPERSEDED 1 · UNVERIFIABLE-from-the-tree 14.**

### R3. `outcome_potential_why` — all 32, and the 8 that carry checkable arithmetic

`PRIMARY`. Most of this field is grading judgement, not a checkable assertion. Eight records state route arithmetic, and **all eight reconcile exactly**:

| record | assertion | measured from `routes.json` today | grade |
|---|---|---|---|
| PUB-SURFACE-TARGETS | "Two of six routes remain open" | 6 routes; `closure_kind == open` → RT-PRAME-IMMTAC, RT-FAP-RLT = **2** | **SUPPORTED** |
| PUB-DEGRADER | "Three of its five routes are instrument-limited" | 5 routes; `instrument_limit` → RT-DEGRADER, RT-COVALENT-PROBE, RT-UBIQ-SELECTIVE = **3** | **SUPPORTED** |
| PUB-NEOANTIGEN | "Both routes closed (premise_false, instrument_limit)" | 2 routes; kinds are exactly those two | **SUPPORTED** |
| PUB-HLA-COVERAGE | "its route is premise_false" | RT-VACCINE `premise_false` | **SUPPORTED** |
| PUB-CLOSED-ROUTES | "Seven closed routes" | **7** | **SUPPORTED** |
| PUB-PARKED-MODALITIES | "Every route parked on a capability nobody has" | 5/5 `parked` + `instrument_limit` | **SUPPORTED** |
| PUB-EMC-PROGRAM | "Corrected 2026-08-09: owns ZERO routes of its own — both routes under it carry `role: context`" | RT-TRABECTEDIN and RT-ICI-TKI both `publication.role == "context"` | **SUPPORTED** |
| PUB-MATRIX-ADDRESS | "all three named handles came back unfavourable or unreachable" | 4 routes, all `parked`/`blocked` | **SUPPORTED** |

The remaining 24 are grading prose with no committed artifact that can adjudicate them (e.g. PUB-KINASE-LEADS' *"the ex-vivo screen hit survives"* — RT-ALK-HIT is `parked`, and whether that counts as "survives" is a judgement, not a measurement).

**Tally (32): SUPPORTED 8 · SUPERSEDED 0 · UNVERIFIABLE 24.**

### R4. The one SUPERSEDED field, and its fan-out measured W06i's way

`PRIMARY`. `systems/graph/publications.json:286`, `PUB-KINASE-LEADS.what_it_would_claim`, quoted whole:

> "Four kinase-directed observations specific to this disease exist in the published and curated record — one reported as expressed and activated, one positive across a small series with an internal control, one an interaction curated on the driver protein itself, one an ex-vivo screen hit — **and none has been followed up by anyone, in a disease with no targeted agent.**"

**Artifact it describes:** none — `document` is `null`, `state: outlined`. It describes the *published record*, and this repository has since read a follow-up into `systems/graph/routes.json:6584` (PMID 29937513 / PMC6073125, Urbini et al. 2018, same authors as the 2014 activation report, quoted verbatim there). W09f established this; I did not re-derive it and did not fetch the source.

**Fan-out — 6 printings across 6 files, 1 hand-written + 5 generated:**

| kind | `file:line` |
|---|---|
| **source (hand-written)** | `systems/graph/publications.json:286` |
| generated | `systems/views/L2-rt-sgk1.md:99` |
| generated | `systems/views/L2-rt-dnapk.md:102` |
| generated | `systems/views/L2-rt-ret.md:101` |
| generated | `systems/views/L2-rt-alk-hit.md:103` |
| generated | `systems/views/L3-publications.md:431` |

Exactly W06i's structure: the four L2 views are the four routes filed against this endpoint (RT-SGK1, RT-DNAPK, RT-RET, RT-ALK-HIT), rendered by `systems_check.py:3045`, plus the L3 index by `:3238`. Tree-wide `git grep -ln "none has been followed up by anyone"` with the campaign directory excluded returns **exactly these six files and nothing else** — no manuscript, no second graph file, no test. **One edit at `:286` plus `--write-views` fixes all six; five view edits fix none of them durably and turn `[G2]` red.**

### R5. PUB-TCIP re-measured today — SUPPORTED, and case-sensitivity is load-bearing

`PRIMARY`, run by me at HEAD `606d79f9`. The field states a measurement dated 2026-08-07. Re-run:

| artifact | `'NR4A3'` case-sensitive | `'nr4a3'` case-insensitive | `'8XTT'` |
|---|---|---|---|
| `research/modalities/nr4a3-induced-interface-census.json` | **0** | 1 | **0** |
| `research/manuscripts/tcip/tcip-interface-floor-sizing.md` | **0** | 20 | **0** |
| `research/modalities/nr4a3-tcip-reach.json` | **3** | 30 | **0** |

The field's quoted-token claim ("'NR4A3' appears 0 times") is **exact**; "The reach enumeration IS NR4A3-anchored but **names it three times**" is **exact**; the 8XTT half holds in all three. All four ratio values (0.896, 1.121, 1.254, and the 6-of-15) are present in the preprint. ⚠ The case-insensitive counts differ only because lowercase `nr4a3` appears in filenames and paths inside those files — a reader re-checking with `grep -i` will get 1/20/30 and wrongly conclude the field is stale. Worth a note beside it; the field is right.

### R6. PUB-VACCINE-PATH — a small derived-value mismatch, **not** a supersession

`PRIMARY`. `publications.json:551`: *"moves to zero at a **0.125**-unit change in an undefended acceptance threshold."* Its own document, `research/manuscripts/neoantigen/emc-vaccine-development-path.md:343`: *"the function is then flat from 0.4580 all the way to the cut; and **it reaches zero 0.1264 below it**."*

`0.125 ≠ 0.1264`, and 0.1264 does not round to 0.125 (it rounds to 0.126). I checked the ordering rather than assuming it: `git log -S'0.1264' -- <doc>` and `git log -S'0.125-unit' -- systems/graph/publications.json` both return the **same single commit** `14a3f172` (2026-09-04). So this is a transcription/rounding imprecision introduced in one commit, **not** a claim overtaken by a later measurement. It nonetheless breaks `CLAUDE.md` §1 (*keep derived values tied to their source*), it is printed into 2 views, and the smallest correct fix is one character in `publications.json:551`.

### R7. Structural finding — the fan-out multiplier, measured for all 33

`PRIMARY`. Probing each record's `what_it_would_claim` head-70 characters across `systems/views/*.md`:

| statistic | value |
|---|---|
| total view printings of `what_it_would_claim` | **116** across 33 records |
| mean views per record | **3.5** |
| maximum | **8** (PUB-CLOSED-ROUTES) |
| PUB-MORTALITY-MECHANISM | **7** — reproduces W06i's count independently (6 L2 + 1 L3) |
| PUB-SURFACE-TARGETS | 7 |
| PUB-BIOMARKER-DEP / PUB-DEGRADER / PUB-PARKED-MODALITIES | 6 |
| minimum | 2 (17 records) |

So W06i's seven-fold fan-out is not exceptional — it is one of five records at 6+, and the *median* record still prints into three files. **A one-line edit in `publications.json` moves 3.5 generated lines on average.**

**Control, confirming W06i's and W09h's zero-consumer finding for `outcome_potential_why` by an independent route:** five distinctive phrases from five different records' `outcome_potential_why` (*"Three of four leads were demoted"*, *"Two of six routes remain open"*, *"Three of its five routes are instrument-limited"*, *"Seven closed routes"*, *"Every route parked on a capability nobody has"*) → **0 views each, 5/5**. The field is required, hand-written, 33 instances, and renders nowhere.

⭐ **The consequence for the owner:** the two fields have opposite defect economics. A stale `what_it_would_claim` is printed 2–8 times and is the first thing a reader of any route view sees; a stale `outcome_potential_why` is invisible outside the JSON. Auditing effort should follow the fan-out, not the field count.

---

## Validation evidence

### RUN

Environment: container `container_0166QEHnXrRA8nCR59c9UG4k`, Linux 6.18.44-fc-v24, `cwd=/home/user/Rare-cancers`, Python 3.11, no network. `git status --porcelain` = 0 lines at start and end. All commands read-only; all exited 0 except the two noted.

```
git rev-parse HEAD                       # 606d79f9… start ; 063f00fa… end
git diff --stat 606d79f9 063f00fa -- systems/graph/publications.json systems/views/ \
    research/manuscripts/ research/modalities/
                                          # (no output) — nothing I measured moved
```

Denominator:

```
python3 -c "…json.load(open('systems/graph/publications.json'))…"
<class 'list'> 33
n_records 33 what_it_would_claim 33 outcome_potential_why 33
```

Numeric reconciliation (instrument 1), final pass:

```
PUB-ENDPOINT.what_it_would_claim: MISSING=['2715', '2851']  (of 20)
PUB-NEOANTIGEN.what_it_would_claim: MISSING=['231']  (of 1)
PUB-VACCINE-PATH.what_it_would_claim: MISSING=['0.125']  (of 1)
PUB-MORTALITY-MECHANISM.outcome_potential_why: MISSING=['214', '742257']  (of 6)   # excluded record
```

— i.e. **28 of 31 checkable numeric field-instances reconciled on the first pass**; all three residuals resolved by hand (comma formatting; a stale line anchor; a rounding mismatch).

`2851`/`2715` resolved:

```
grep -n "95.2\|2,851\|2,715" research/manuscripts/endpoint/response-endpoint-indolent-tumours.md
84:constraint: of 2,851 trials naming best overall response, 2,715 (95.2%) omitted the four
444:| trials naming best overall response | 2,851 | 2,715 | 95.2% |
```

PUB-TCIP re-measurement:

```
for f in …census.json …floor-sizing.md …reach.json; do
  echo "$f: NR4A3=$(grep -o 'NR4A3' "$f" | wc -l)"; done
research/modalities/nr4a3-induced-interface-census.json: NR4A3=0
research/manuscripts/tcip/tcip-interface-floor-sizing.md: NR4A3=0
research/modalities/nr4a3-tcip-reach.json: NR4A3=3
grep -n 'NR4A3' …census.json    # (no output, exit 1)
grep -n 'NR4A3' …floor-sizing.md # (no output, exit 1)
```

Stale pointer:

```
sed -n '231p' research/modalities/fusion_breakpoints.py
    single-junction artifact counted 38 spanning peptides at EWSR1 e7 :: NR4A3 e3 and this module
grep -n "parent" research/modalities/fusion_breakpoints.py
29:  4. For each emitted junction, take junction-spanning 8-11mers absent from both parent
224:    codon there IS a novel residue at `j0` (belonging to neither parent) and the tumour-specific
```

⚠ Stated precisely so it is not overclaimed: `:231` falls **inside** the docstring block (≈`:218-239`) whose subject *is* the parent/novel-residue definition, but the line itself is a sentence about a 38-vs-34 peptide-count consolidation dated 2026-08-07, not the parent-comparison test. The anchor is adjacent-but-wrong, not flatly false; the substance of the claim holds.

Route arithmetic (instrument 3), verbatim excerpt:

```
RT-TRABECTEDIN | publication={'endpoint':'PUB-EMC-PROGRAM','role':'context',…} | closure_kind=open
RT-ICI-TKI     | publication={'endpoint':'PUB-EMC-PROGRAM','role':'context',…} | closure_kind=open
RT-SCHEDULING  | …'PUB-STRATEGY-ARCH','role':'contributing'… | closure_kind=definitional
RT-SEQUENCING  | …'PUB-STRATEGY-ARCH'…                        | closure_kind=instrument_limit
PUB-SURFACE-TARGETS: n=6 ; closure_kind==open → RT-PRAME-IMMTAC, RT-FAP-RLT
PUB-DEGRADER: n=5 ; instrument_limit → RT-DEGRADER, RT-COVALENT-PROBE, RT-UBIQ-SELECTIVE
PUB-CLOSED-ROUTES: n=7 ; PUB-PARKED-MODALITIES: n=5 (all parked, all instrument_limit)
```

Fan-out (instrument 4):

```
git grep -ln "none has been followed up by anyone" -- . ':!research/autonomy/opus-capacity-campaign-20260908/**'
systems/graph/publications.json
systems/views/L2-rt-alk-hit.md
systems/views/L2-rt-dnapk.md
systems/views/L2-rt-ret.md
systems/views/L2-rt-sgk1.md
systems/views/L3-publications.md
```

with exact lines `:286`, `:103`, `:102`, `:101`, `:99`, `:431` read individually.

`outcome_potential_why` zero-consumer control:

```
views carrying [Three of four leads were demoted]: 0
views carrying [Two of six routes remain open]: 0
views carrying [Three of its five routes are instrument-limited]: 0
views carrying [Seven closed routes]: 0
views carrying [Every route parked on a capability nobody has]: 0
```

Scratch teardown:

```
rm -rf /tmp/claude-0/w06j && ls -d /tmp/claude-0/w06j
ls: cannot access '/tmp/claude-0/w06j': No such file or directory
```

Two non-zero exits, both benign and recorded: `cat reports/W06i-…` → exit 1 (dispatch path wrong, see Prior-work check); the final compound command → exit 2 from `ls` on the just-deleted scratch directory.

### PROPOSED (NOT RUN)

- `python3 systems/systems_check.py --check` and `--write-views` — **NOT RUN**, forbidden by dispatch and pointless against a tree I must not modify. The generated/hand-written classification here rests on documentary evidence (declared `generator:` front matter, the `:3045`/`:3238` emit sites read in source, byte-identical text), exactly as W06i's did, **not** on an execution proof. W09d/W09e/W09f/W26b did run the generator in scratch copies; I deliberately did not duplicate that.
- Any correction to `publications.json:286`, `:551`, or `:404` — **NOT AUTHORED**, not drafted as a patch. Repair is the owner's.
- Independent retrieval of PMID 29937513 to re-confirm W09f's refutation — **NOT RUN**, no network, and CLOSED-WORK forbids replaying routes.

---

## Limitations

- **Supersession is only detectable where the tree holds an artifact that can contradict the claim.** 38 of 64 field instances are UNVERIFIABLE-from-the-tree, and that is the honest majority. Most are world-scoped ("never been asked by anyone", "the field publishes almost none") or pure grading judgement. A stale claim hiding in one of those 38 would be invisible to every instrument I used. **UNVERIFIABLE means unknown, not clean.**
- **My four instruments have known blind spots.** Numeric reconciliation catches only claims carrying digits present in a named document, misses semantic drift entirely, and would pass a number that is right in both places and wrong in the world. Route arithmetic catches only counts a field states explicitly. Fifteen records have `document: null` and are unreachable by instrument 1 altogether.
- **I inherited rather than re-derived W09f's verdicts** on PUB-KINASE-LEADS, PUB-ANDGATE, PUB-FUSION-OUTPUT, PUB-EMC-CLASSIFICATION and PUB-LOCOREGIONAL. If W09f's reading of `routes.json:6584` were wrong, my single SUPERSEDED row falls with it — my independent contribution to that row is the **fan-out**, which stands either way.
- **Tracked working tree only, at one HEAD.** No `.git` history search beyond two `git log -S` ordering checks, no untracked files, no frozen corpus. A claim superseded at `93b` but restored since is out of scope by design.
- **Campaign reports excluded by pathspec** from every census grep; sibling reports quote these fields repeatedly and are evidence *about* the fields, not printings to repair.
- **PUB-MORTALITY-MECHANISM was not audited** (dispatch), though it appears in R7's fan-out table as an independent reproduction of W06i's count.
- This unit establishes **nothing scientific about EMC**. It makes no claim about mortality, efficacy, safety, selectivity, therapeutic window or clinical readiness, touches no patient data, retrieved no source, and asserts no new biology. It is a records-integrity measurement.

---

## Stop condition

**Set up front:** return as soon as (i) every in-scope `PUB-*` record is graded on both fields against a stated instrument, (ii) an honest denominator separates graded from ungradeable, (iii) every SUPERSEDED row carries a measured fan-out across `systems/views/`, and (iv) the `outcome_potential_why` no-consumer finding is independently controlled — or at ~40 tool calls / ~40 minutes, whichever first.

**MET on all four**, at 30 tool calls and 4.5 minutes. Returning early. No repair authored, no patch drafted, no file edited, no generator executed.

---

## Tool-call and wall-clock count actually used

**30 tool calls** (27 `Bash`, 2 `Read`, 1 `Skill`-free — no Grep, no network tool). No content-policy refusal was encountered on any branch; no harness permission refusal either.

**Wall clock: 4 min 29 s** (`03:45:16Z` → `03:49:45Z`). Budget was ~40 calls / ~40 min.

---

## Next concrete action

**For the graph owner — three edit sites in `systems/graph/publications.json`, in descending order of blast radius, none of them mine to make:**

1. `:286` PUB-KINASE-LEADS — the SUPERSEDED clause; **6 printings across 6 files**; W09f already supplies a smallest-correct restatement backed by `routes.json:6584` and the peer-review wording rule at `emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md:424`.
2. `:551` PUB-VACCINE-PATH — `0.125` → `0.1264` to match `emc-vaccine-development-path.md:343`; 2 printings; a one-character-class fix that restores the §1 derived-value tie.
3. `:404` PUB-NEOANTIGEN — re-anchor `fusion_breakpoints.py:231` to the line that actually carries the parent comparison (`:29` for the rule, `:224` for the novel-residue definition); 3 printings.

Each requires `python3 systems/systems_check.py --write-views` in the same change to keep `[G2]` green.

**One specific successor task for this lane.** R7 measures a per-record fan-out of 2–8 view lines from a single hand-written field, and R3 measures **zero** for a required sibling field on the same records — yet no check anywhere compares either field against the artifact it describes. The bounded, read-only successor is: **measure whether the `documents` these records name are themselves reachable and current — i.e. for all 33 records, does `document.file` exist, does `document.anchor` resolve inside it, and does the manuscript's own front-matter state (`status:`, `superseded:`) agree with the record's `state:` field?** My instrument 2 found only four file pointers *inside* the two prose fields, but the structured `document` object was outside my dispatch and is the obvious next place a stale pointer hides, with the same 3.5× print multiplier behind it. It is tree-local, needs no network, and no sibling report in this campaign has touched it.
