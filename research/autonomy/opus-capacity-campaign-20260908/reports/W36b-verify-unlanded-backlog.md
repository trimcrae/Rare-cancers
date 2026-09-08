<!-- collected 2026-09-08T04:32:14Z by campaign coordinator; agent id a8df17963cfca24b5; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a8df17963cfca24b5.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W36b**, verification successor to W36 (routed-repair index status verification), OPUS-CAPACITY-CAMPAIGN-20260908. Read-only; I performed, applied, sequenced and decided nothing. I inherited W36's classification, conflicts and ranking without re-deriving them.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. I did not observe the served model; no environment variable in this container names a model. The coordinator must extract the actual per-child runtime model from the transcript.

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
GLOBAL_AGENT_NO_PROXY=<same list as no_proxy>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<proxy/truststore flags>
NO_PROXY=<same list as no_proxy>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same list as no_proxy>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**Start:** `date -u` = `Tue Sep 8 03:44:56 UTC 2026`; `git rev-parse HEAD` = `606d79f96526b651f3b825190d721f6b302c032e`; `git status --porcelain` = 0 lines.
**End:** `date -u` = `Tue Sep 8 03:52:13 UTC 2026`; `git rev-parse HEAD` = `cfc5f3dcbfccf4e05e8316be16f55d129826eb3a`; `git status --porcelain` = 0 lines.

**HEAD moved under me** (`606d79f9` → `cfc5f3dc`, both coordinator collections). I did not assume nothing changed: I re-ran `git diff --name-only 92abbcb HEAD | grep -v opus-capacity-campaign-20260908 | wc -l` → **0** at the end HEAD, and re-ran three spot measurements at the end HEAD (`nobody followed up` → 1, `PYTHONUTF8` in preflight → 0, `W23b` in WAVE-LOG → 0), all reproducing. Nothing I measured changed.

## Question

Exactly W36's named next action: **for the ~84 rows W36 marked `T` (transcribed from a report, never checked), does the proposed field/line/row/file exist at HEAD?** — and, with those checks added to W36's 19, what is the campaign's first real resolution-rate denominator: of N routed items checked, how many are landed?

Open because W36's headline "zero landed" rested on **eleven** tree-verified spot-checks out of 103 index rows (U01–U102 plus U02a). A resolution rate on n=11 is not a rate.

## Prior-work check

Read **in full**: `research/autonomy/opus-capacity-campaign-20260908/COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, and `reports/W36-routed-repair-index.md` (366 lines).

- The index does **not** live at `reports/W36-routed-repair-index.md` as my dispatch writes it; `find / -name 'W36-routed-repair-index.md'` resolves it at `/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/reports/W36-routed-repair-index.md`. I did not guess; I located it.
- I used the brief's "Known, measured, and NOT worth rediscovering" section: I did **not** run `scripts/preflight.sh`, and I did not spend a run attributing the systems-step baseline.
- **W25 untouched.** I read, audited, extended and referenced no `W25-*` material. (`executed-artifacts/W25` exists in the campaign directory; I did not open it.)
- **Zero network calls.** No closed retrieval route replayed: I checked whether requested sources are *committed in the tree*, never attempted to fetch one.
- I inherited W36's classification, conflicts (16 pairs) and ranking unchanged, and re-derived none of them.

## Method and inputs

For each `T` row I ran one read-only tree check — `grep`/`grep -c`, `sed -n`, `python3 -c` JSON read, `git ls-files`, `git grep -l`, or `ls`/`test -e` — against the named target at HEAD. Where the index did not carry the proposed string, I read the originating report's own proposal (`W09c`, `W09e`, `W09g`, `W16d`, `W17c`, `W17e`, `W19b`, `W26`, `W03e`, `W06b`, `W05f`, `W20d`, `W20g`, `W03d`) and grepped for that string specifically, so the check tests the item, not the file's existence.

**One structural check underpins all of them:** at both my start and end HEAD, `git diff --name-only 92abbcb HEAD | grep -v opus-capacity-campaign-20260908` returns **0 files** (186 files changed in total, every one inside the campaign directory). No repository file outside the campaign directory has changed since the campaign's start commit. This is corroboration, not a substitute — the per-item greps also test whether a report's *premise* was already false before the campaign, which the diff cannot.

Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, Python 3.11.15, cwd `/home/user/Rare-cancers` (read-only use), scratch `/tmp/claude-0/w36b` (created, never written into, deleted — `SCRATCH DELETED` confirmed). No repository write, no git write operation, no network.

## Result

### The denominator

| Quantity | Count |
|---|---|
| Index rows total (U01–U102 + U02a) | **103** |
| Rows checked against the tree — W36's 19 + my 84 | **103 (100 %)** |
| **Checkable by inspection and checked** | **89** |
| **`V` — confirmed still unlanded** | **87** (my 69 + W36's 18) |
| **`V*` — landed since its report, or premise false at HEAD** | **2** (W36's U22; my U05) — **neither is a landed change** |
| **`UNKNOWN` — not checkable by inspection** | **14** (all mine; W36 marked none) |
| **LANDED** | **0** |

**The campaign's first real resolution-rate denominator: of 89 routed items checkable and checked at HEAD, 0 are landed — 0/89 (0 %).** W36's "zero landed" rested on eleven; it now rests on eighty-nine. Both `V*` rows are false-premise findings (a report described the tree wrongly), not repairs that landed: **no proposed change in the index is present at HEAD.**

### My 84 rows, re-marked

**Tier 1 — `systems/graph/` and active manuscripts (14 rows): 12 `V`, 1 `V*`, 1 `UNKNOWN`** · all `PRIMARY` (tree state I read)

| # | Mark | Evidence at HEAD |
|---|---|---|
| U01 | V | `grep -c 'does not appear in this histology anywhere' systems/graph/artifacts.json` → **1**; `ART-RT-CONTRADICTION` and `ART-CARE-DELIVERY-EVIDENCE` notes both present and unchanged (W09c's RED acceptance test's two subjects still stand) |
| U02 | V | `publications.json:119` still carries the C5 clause — `sed -n '119p'` contains both `known before the operation` and `treatment setting` |
| U02a | V | Same target, same state; the W09d/W09e status disagreement is unresolved in the tree either way |
| U03 | V | `sed -n '287p' systems/graph/publications.json` → `"working_title": "Four kinase observations … that nobody followed up"`, byte-identical to W09g's "before" |
| U04 | V | 33 `outcome_potential_why` fields on 33 records; `grep -c outcome_potential_why systems/systems_check.py` → **0** (the "no consumer" premise holds; no schema change) |
| U05 | **V\*** | **Premise false at HEAD.** W09f routes the audit onward to "the same names across `routes.json`, `strategies.json`, `modalities.json`, `objects.json`". Per-file per-name counts: `outcome_potential_why` 0/0/0/0, `working_title` 0/0/0/0, `"_evidence"` 0/0/0/0. **The second half of the proposed audit has no subject in those four files.** The `publications.json` half remains genuinely unaudited |
| U07 | V | 9 of W26's 10 named OVER-SCOPED lines render the described field verbatim (`:3624`, `:3667`, `:3672`, `:3698`, `:1166`, `:6800`, `:7939`, `:8586`, `:8281`). ⚠ `:6821` renders `"role": "primary"`, not `remaining_unknowns[1]` — a line-pointer offset in the report, not a change in the file |
| U08 | V | `grep -c 'three independent' systems/graph/routes.json` → **3**; the manuscript sentence stands at `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md:1081` and `fusion-output-graph-records.json:212`. **W36's path note confirmed**: the path W05b writes does not exist |
| U09 | V | `grep -rln 'NR4A2-fusion subset' research/ --include=*.md` outside the campaign dir → **no hits**; caveat A is at none of its six locations |
| U10 | V | `aso-citations-priorart-2026-08-08.md:140` still files PMID 41315062 inside the `Variant 5′ partners:` bullet. Nuance both files already carry: the entry itself says "not NR4A3" / "rather than NR4A3", so the defect is list placement, not a false sentence |
| U12 | **UNKNOWN** | The item routes an *unattributable baseline*, not a named change — there is no tree predicate that distinguishes landed from unlanded. Adjacent measured fact: `DOC_SKIP` appears **8×** in `systems_check.py` (pre-existing) and **0×** in `preflight.sh`, consistent with COMMON-BRIEF's statement that no campaign exclusion was added |
| U14 | V | `grep -c 'Welch df carried in each contrast block'` → **0**; `sed -n '564,568p'` shows the sentence still without a named distribution |
| U16 | V | `grep -c` in `pinned-figures.json` for W16d's own entry ids `emc_locoregional_metastasis_pct` and `…_events` → **0** and **0** |
| U18 | V | `lint_consistency.py:456-460` — `_dig_json` still `for part in dotted.split(".")` with no bracket or escape support |

**Tier 2 — protected shared state and the commit gate (11 rows): 11 `V`**

| # | Mark | Evidence at HEAD |
|---|---|---|
| U23 | V | `PMC4946242` present 3×; the citation block at `:944 ff.` still carries `"verified": true`; neither contradicted field corrected |
| U24 | V | `python3 -c` JSON read: `registry.cohorts` n=14, **`cohorts[8].sourceId == "remiszewski2025"`** — not repointed |
| U25 | V | `grep -c bishop2019` → **3**; the clause stands, no admissibility-rule change |
| U27 | V | Same greps as U26: `PYTHONUTF8` **0**, `PYTHONIOENCODING` **0** in `scripts/preflight.sh` |
| U30 | V | `scripts/validate-registry.mjs:88` still reads `if (c.pool === false && !c.contextReason) warns.push(…)` |
| U31 | V | `grep -c GUARDED-NOT-ENFORCED scripts/preflight.sh` → **0** |
| U32 | V | `grep -c -E 'emc_mortality_decomposition\|emc_relative_survival\|emc_terminal_events\|emc_rt_bed_reappraisal' scripts/preflight.sh` → **0** (also re-confirms W36's U28/U29) |
| U33 | V | `grep -c lint_absence_claims scripts/preflight.sh` → **0**. ⚠ Also: `git ls-files \| grep lint_absence` → **no tracked file** — the tool to be wired does not exist in the tree |
| U34 | V | `grep -c examined scripts/preflight.sh` → **0**; no per-row examination count |
| U35 | V | `scripts/regenerate_aso_chain.sh` calls `python3 $MOD/aso_noncoding_acceptor_screened_table.py` with an **empty** argument string — no `--check` |
| U36 | V | `grep -c _render research/manuscripts/submission_citations.py` → **0**; W03e's `_render(order, meta, missing, bare)` extraction not present |

**Tier 3 — generators, artifacts and tests (31 rows): 28 `V`, 3 `UNKNOWN`**

| # | Mark | Evidence at HEAD |
|---|---|---|
| U37 | V | `emc_fourth_cohort_quant.py` `--check` block unchanged: `argparse --check` at `:916`, `"--check: no committed artifact…"` at `:936`, drift tuple at `:939-941`. Neither R07's nor R08's repair present |
| U38 | V | Same file; C3's `probe_counts_sha256` still absent from the tuple (re-confirms W36's U39) |
| U40 | V | `:583` still `probes = sorted(set().union(*[set(runs[a]["counts"]) for a in accs]))` — union, not the intersection filter |
| U42 | V | `grep -c -- '--check' research/manuscripts/emc_mortality_decomposition.py` → **0** |
| U44 | **UNKNOWN** | No target of its own; it only names U43's shape. U43 verified absent by W36 |
| U45 | V | `--check` count **0** in both `emc_relative_survival.py` and `emc_terminal_events.py` |
| U46 | V | `sed -n '599p'` is byte-identical to W06b's "before" string; the proposed continued form absent |
| U47 | V | `emc_systemic_therapy_pooling.py:701-703` still carries the pre-repair wording ("published 48% is the whole mixed-histology stage-1 cohort…") |
| U48 | V | `pool_reason` still `same_registration_as_immunosarc2_and_emc_subset_not_separately_reported`; `why_excluded` window clause unchanged |
| U49 | V | `grep -c -E '"design"\|confirmation' emc-mortality-decomposition-inputs.json` → **0** |
| U50 | V | `grep -c 'def build' emc_locoregional_eligibility.py` → **0**. Note: `research/modalities/tests/test_locoregional_eligibility.py` already exists (pre-campaign), so this is an added function in an existing file, not a new file |
| U51 | **UNKNOWN** | The stale-side determination needs GEO series matrices (no network, no runner). Thirteen panel test files pre-date the campaign, so "no identity test added" is not separable from "already there" by inspection |
| U53 | V | JSON read: `candidate_sources` n=17, **16 carry `overlap_risk`, `[0]` does not** |
| U54 | V | `emc-fourth-cohort-route-readout.json:14` still the inherited `"⛔ _what_a_false_row_is_not"` sentence |
| U55 | V | `grep -c SUPERSEDED emc-rt-bed-reappraisal.json` → **0**. ⚠ `:41` renders a `"read_from"` field, not a "false clause" — that line pointer does not resolve as W10f writes it, and I do not guess the intended line |
| U56 | V | `emc_radiotherapy_contradiction.py:273-275` still the `denominator_means` block described; no V5 edit |
| U57 | V | `grep -n I6 emc_radiotherapy_contradiction.py` → no hits; invariant not added |
| U58 | V | `denominator_means` still written in three modules (1 / 3 / 2 occurrences) — the three-writer premise holds, nothing changed |
| U59 | V | `emc-surgical-quality.json` unchanged (3 absence-form strings); no C3/C4/C6 correction landed. Coarse check — the report gives no exact string |
| U60 | V | `grep -c manifest scripts/validate-registry.mjs` → **0**; heuristic aggregate discovery unreplaced |
| U61 | V | `grep -c alignment research/modalities/emc_atr_vulnerability.py` → **0**; no alignment contract |
| U64 | V | `ls research/modalities/tests/ \| grep -iE 'welch\|atr_point\|variance_inversion\|df_identity'` → **empty** |
| U65 | V | Same listing; none of the three modules promoted |
| U66 | V | `aso_delivery_antigen.py:381` still `abs(re_["t"] - got) > 0.02` — the flat tolerance |
| U67 | V | `:837-839` still compares `per_antigen` and `headline` field-wise, not whole-document |
| U68 | V | `git ls-files \| grep -iE 'publish-vs-gate\|module-census'` → **no tracked census artifact** |
| U70 | V | `tier_budget.py:78-86` — `count_dir` still `os.listdir(path)`, non-recursive |
| U71 | V | **Target path resolved** (W36's index gives only "ASO screen loader"): `research/modalities/aso_per_junction_table.py:278` — `_load` still `if not os.path.exists(path): return {}`, the silent misattribution |
| U72 | V | All four of W20d §6's "current" strings still stand verbatim: `The hypothesis is REFUTED` (W20, 1), `absent from this panel` (W20, 1), `1,645 probe sequences already committed` (W20c, 1) |
| U73 | V | `emc_fourth_cohort_quant.py:586` still `g = (gene_of or {}).get(pr) or "unassigned"`; `multi_gene`/`not_offered` count **0** |
| U74 | **UNKNOWN** | Target is an MCP tool's behaviour, not a repository file — not checkable by tree inspection |

**Tier 4 — campaign-artifact corrections (14 rows): 12 `V`, 2 `UNKNOWN`.** These targets are *inside* the campaign directory, which does change, so the git-diff corroboration does not apply and each was checked directly.

| # | Mark | Evidence at HEAD |
|---|---|---|
| U75 | V | `grep -c W23b WAVE-LOG.md` → **0**; no such correction block (file 451 lines, latest correction dated ~02:58Z) |
| U76 | V | `grep -c -i junction` in `COMMON-BRIEF.md`, `AGENT-ROLES.md`, `MANIFEST.md` → **0 / 0 / 0**; the dispatch text is unfixed |
| U77 | V | `W21b:145` still the N2 row as written; 0 appended corrections in W21b |
| U78 | V | `W07:173` still asserts *"EMC treatment toxicity has never been reported with an EMC-specific denominator."* — no strike-through; 0 corrections appended to any W07* report |
| U79 | V | `W07e:158` Axis-R row for `27418251` unchanged; 0 corrections appended |
| U80 | V | `W07e` §5.5 at `:196` unchanged; 0 corrections appended |
| U81 | V | `W07g:161` unchanged; 0 corrections appended |
| U82 | V | `grep -c -i 'focused correction\|CORRECTION APPENDED' W08f*.md` → **0** |
| U83 | V | 0 corrections in the lane-4 reports. ⚠ `W04c:196` is a **blank line** — that report:line pointer does not resolve as W36's index writes it; I do not guess the intended line |
| U84 | V | `evidence/` in the campaign directory is **empty**; no reachability record carrying the four CLOSED-WORK-only routes |
| U85 | V | `44–63 obtainable` still stands at `W01e:174` and `W01f:79,136` — not retired |
| U86 | **UNKNOWN** | The 71-unanchored-identifier count is a measurement I did not re-run, and no anchor-checking tool is tracked |
| U87 | V | The U17 half is still unlanded (`fusion-junction-neoantigen-paper` → **0** in `pinned-figures.json`); the file still carries **102** `must_appear_in` guards, none removed |
| U88 | **UNKNOWN** | Partially overtaken and not separable: `reports/` held **150** files when W36 ran, **182** at my start HEAD and **189** at my end HEAD. Collection clearly continued, but I did not verify that the specific 21 workers W22b named are among them |

**Tier 5 — measurement and retrieval requests (14 rows): 6 `V`, 8 `UNKNOWN`.** For these I read "landed" as *the requested material is committed in the tree*; I made no retrieval attempt of any kind.

| # | Mark | Evidence at HEAD |
|---|---|---|
| U89 | V | `git grep -l PRJNA692081 -- ':!<campaign dir>'` → **0 files**; the Brenca deposit accession is not committed |
| U90 | **UNKNOWN** | Needs an Actions runner; no tree predicate |
| U91 | V | Neither `GSE24369_series_matrix.txt.gz` nor `GSE4303-GPL3290_series_matrix.txt.gz` is a tracked file (`git ls-files` → none) |
| U92 | V | `PMID 11493979` (Oshiro 2000) → **0 files** in the tracked tree outside the campaign dir |
| U93 | **UNKNOWN** | A coordinator ruling, not a tree object. ⚠ It is a question, **not an authorization**, and I treated it as such |
| U94 | **UNKNOWN** | Vendor probe manifest behind a recorded egress denial; nothing to inspect, and I probed no route |
| U95 | **UNKNOWN** | Requires running `phase_map` at k=2 (runner); no matching artifact tracked |
| U96 | V | No re-read artifact; the `PMC4946242` registry citation is unchanged and still `"verified": true` |
| U97 | **UNKNOWN** | `PMC8776602` and `PMC7237692` each appear **11×** in the tracked tree — but an identifier's presence does **not** establish that its full text was retrieved. Not decidable by inspection |
| U98 | **UNKNOWN** | "no permitted route"; nothing in tree to check |
| U99 | V | `PMID 19890812` → **0 files** in the tracked tree outside the campaign dir |
| U100 | **UNKNOWN** | Closed at source; no tree predicate |
| U101 | **UNKNOWN** | Deliberately not run; and W18b records a classifier block I did not route around |
| U102 | V | **0** tracked `.bed` files; `GSE243553` appears 31× as a reference, but no marker BEDs are committed. Adjacent to HELD W25 material — not touched |

### Two findings beyond the tally

1. **A structural fact that makes 0/89 unsurprising and stronger than a sample:** at both my HEADs, `git diff --name-only 92abbcb HEAD` outside the campaign directory is **empty**. In this campaign, **no repository file outside `research/autonomy/opus-capacity-campaign-20260908/` has changed at all.** Every Tier-1/2/3 item (74 of the 103 rows) therefore *could not* have landed, independently of my greps. This is the same guarantee COMMON-BRIEF flags as ending silently if a coordinator commit ever touches anything outside that directory — it still holds at `cfc5f3dc`.
2. **A second false premise, joining W36's U22 (`evidenceQuestions`):** U05's onward audit names four graph files that contain **none** of the three field names it proposes auditing. Two of 89 checked rows rest on a premise that is false at HEAD — a ~2 % report-premise error rate, measured, not estimated.

### Three report:line pointers that do not resolve as written

Reported, not guessed (adding to W36's two): **U07's `routes.json:6821`** (renders `"role": "primary"`, not `remaining_unknowns[1]`); **U55's `emc-rt-bed-reappraisal.json:41`** (renders a `read_from` field, not a false clause); **U83's `W04c:196`** (a blank line). Separately, **U33's tool `lint_absence_claims.py` is not a tracked file**, and **U71's target ("ASO screen loader") carries no path in the index** — it resolves to `research/modalities/aso_per_junction_table.py:278`.

## Validation evidence

All `RUN`, all read-only, all at `/home/user/Rare-cancers`, exit 0 unless noted. Nothing `PROPOSED (NOT RUN)`; no test authored, no gate touched, `scripts/preflight.sh` never invoked, `atr_hrd_sarcoma_series.py` never invoked.

Representative verbatim outputs (each item's command is quoted in its Result row):

```
$ git diff --name-only 92abbcb HEAD | grep -v 'opus-capacity-campaign-20260908' | wc -l
0                                    # at 606d79f9 (start) and cfc5f3dc (end)
$ git diff --name-only 92abbcb HEAD | wc -l
186

$ sed -n '287p' systems/graph/publications.json
    "working_title": "Four kinase observations in extraskeletal myxoid chondrosarcoma that nobody followed up",

$ for f in routes strategies modalities objects; do for k in outcome_potential_why working_title _evidence; do grep -c "\"$k\"" systems/graph/$f.json; done; done
0 0 0 0 0 0 0 0 0 0 0 0             # U05: premise false at HEAD

$ python3 -c "...json.load('research/data/emc-clinical-registry.json')..."
cohorts at /registry n= 14
 [8].sourceId= remiszewski2025

$ sed -n '85,92p' scripts/validate-registry.mjs
  if (c.pool === false && !c.contextReason) warns.push(`${cw} is context (pool:false) but gives no contextReason`);

$ sed -n '939,942p' research/modalities/emc_fourth_cohort_quant.py
        drift = [k for k in ("probe_gate", "n_runs_read", "n_probes_common_to_every_read_run",
                             "n_genes_with_at_least_one_assigned_probe", "gene_counts_sha256")

$ sed -n '278,282p' research/modalities/aso_per_junction_table.py
def _load(name, key="per_design", root=None):
    path = os.path.join(root or HERE, name)
    if not os.path.exists(path):
        return {}

$ grep -c 'W23b' research/autonomy/.../WAVE-LOG.md          -> 0   (exit 1, grep no-match)
$ git grep -l 'PRJNA692081' -- . ':!research/autonomy/opus-capacity-campaign-20260908' | wc -l   -> 0
$ git status --porcelain | wc -l                            -> 0   (start and end)
$ rm -rf /tmp/claude-0/w36b; test -d /tmp/claude-0/w36b && echo PRESENT || echo "SCRATCH DELETED"
SCRATCH DELETED
```

The single non-zero exit in the run was `grep -c 'W23b' WAVE-LOG.md` returning **0** (grep's no-match exit 1), which truncated one compound command; I re-ran the remainder rather than suppressing the code. No guard was weakened, no exit code masked.

## Limitations

- **0/89 is a status measurement, not a verdict on the items.** It says no proposed change is present at HEAD. It says nothing about whether any item *should* land, and I adjudicated none.
- **`UNKNOWN` is honest, not zero (14 rows).** Eight Tier-5 retrieval requests, U12, U44, U51, U74, U86, U88 have no tree predicate that separates landed from unlanded, or need a runner/network I do not have. They are excluded from the denominator rather than counted as unlanded.
- **The `V` standard varies in strength.** Rows where the report supplied an exact string (U03, U46, U66, U72, …) are byte-level. Rows where it did not (U59, U54, U01's second node) rest on the file being unchanged plus a coarse content match, and are correspondingly weaker; I flagged those inline.
- **Report-side rows (Tier 4) were checked for an appended correction, not for whether the underlying claim is right.** I did not re-derive any lane's science.
- **I did not verify W36's 18 `V` rows independently**, except where a check of mine incidentally re-covered one (U26 via U27, U28/U29 via U32, U39 via U38, U17 via U87). The combined 87 therefore inherits W36's evidence for 14 of its rows.
- **HEAD advanced mid-run** (`606d79f9` → `cfc5f3dc`; reports 182 → 189 in ~8 minutes). All measurements were re-checked at the end HEAD; none moved. The *growth* half of W36's question is still moving under any measurement of it.
- No clinical, efficacy, safety, selectivity or therapeutic-window claim is made or implied anywhere in this report. There is no wet lab.

## Stop condition

**Set up front:** return as soon as every `T` row in W36's index carries a `V` / `V*` / `UNKNOWN` mark backed by one executed tree check, and the combined denominator is stated — target ~40 tool calls / ~40 minutes.

**MET.** All 84 `T` rows re-marked; denominator stated at 0 landed of 89 checked. Returning immediately; no padding.

## Tool-call and wall-clock count actually used

**19 tool calls** (all Bash, all read-only), **~7.5 minutes wall clock** (03:44:56Z → 03:52:13Z). Well inside both targets.

## Next concrete action

**One successor, and it is a decision, not a measurement:** the index's status question is now closed at 0/89 — re-measuring it is what `CLAUDE.md` §5 forbids. The open lane-adjacent question is the one my Tier-5 and Tier-4 `UNKNOWN`s expose: **fourteen index rows have no tree predicate at all, so no future run can ever mark them landed or unlanded by inspection.** A successor should define, for the eight Tier-5 retrieval requests specifically, what committed artifact would constitute "fulfilled" (a cached full text under `literature/`? a citation with `verified: true` and a `read_from`?) — a definition, written once, that makes the campaign's retrieval surface measurable at all. That is a coordinator/owner definition, not a worker's, and I do not make it here.
