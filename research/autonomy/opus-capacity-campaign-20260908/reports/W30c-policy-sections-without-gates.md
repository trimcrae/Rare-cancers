<!-- collected 2026-09-08T03:49:31Z by campaign coordinator; agent id a1ca09cf25d1ccc2d; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a1ca09cf25d1ccc2d.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted; report follows.

## Worker

**W30c**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: evidence-contract *enforcement map* — extending W30's and W30b's §2.6/§2.7 conformance question to the whole of `systems/POLICY-evidence.md`.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in my environment corroborates it — no variable names a model. The coordinator must extract the served model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`:

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
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy/truststore only)
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

**Start** — `date -u` → `Tue Sep  8 03:41:55 UTC 2026`; `git rev-parse HEAD` → `5ae0fa04ff9516ac8f820381079d644a094f4a77`; `git status --porcelain` → **empty**.
**End** — `date -u` → `Tue Sep  8 03:45:44 UTC 2026`; `git rev-parse HEAD` → `606d79f96526b651f3b825190d721f6b302c032e` (**HEAD advanced under me**, coordinator collecting reports); `git status --porcelain` → **empty**.
**Read integrity across the HEAD move verified**: `git diff --stat 5ae0fa04 606d79f9 -- systems/POLICY-evidence.md scripts/validate-registry.mjs scripts/preflight.sh research/data/emc-clinical-registry.json research/meta/meta-analysis.mjs research/meta/results.json` → **empty output, exit 0**. Every load-bearing input byte-identical.

**Write isolation honoured: zero repository writes, zero git write operations, no network, no retrieval, no MCP call.** One scratch script (`secmap.py`) under `/tmp/claude-0/w30c/`; all other execution was stdin heredocs. `git status --porcelain` empty at start and end. I did not run `scripts/preflight.sh`; I ran **no generator at all** this run (W30b already ran five with `--check`), so no write-free verification was needed; and I did not run `research/meta/meta-analysis.mjs`, which **writes** `research/meta/results.json` via `writeFileSync` — I recomputed its inputs in Python instead. **Scratch directory deleted** (`rm -rf /tmp/claude-0/w30c`; `ls` confirms "No such file or directory").

## Question

**Across all sixteen numbered requirement units of `systems/POLICY-evidence.md` — not just §2.6 and §2.7 — which are enforced by a gate, test or validator, where does that enforcement run, and which have none at all?** And for the sections that actually govern committed artifacts, does the governed artifact conform?

Open because W30 and W30b together covered 2 of 16 units of a 386-line contract, and both found the enforcement question more interesting than the conformance question. Neither established whether §2.6/§2.7's gate hole is a local defect of two new sections or the shape of the whole contract.

## Prior-work check

Commands run (read-only) and what they showed:

```
$ grep -rn "governed_by" --include='*.json' --include='*.py' --include='*.mjs' --include='*.md' .
   → 9 hits (excluding campaign reports), ALL "systems/POLICY-evidence.md 2.6", ZERO naming 2.7
     — reproduces W30b's count exactly, on a later HEAD.
$ grep -rn -o -E "POLICY-evidence(\.md)?[^\"'`]{0,40}" --include=… .   # 118 distinct files
$ python3 /tmp/claude-0/w30c/secmap.py    # section-number attribution across all tracked files
$ grep -rn -l "POLICY-evidence" --include='test_*.py' .    → 10 test modules
$ grep -rn "evidenceQuestions" --include='*.py' --include='*.mjs' --include='*.js' .
   → 2 hits, both scripts/validate-registry.mjs
```

I read `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md` and `CLOSED-WORK.md` in full before reporting, and `systems/POLICY-evidence.md` and `reports/W30b-policy-2.6-2.7-conformance.md` in full before working.

**Confirmed not replayed:** W30b's §2.6/§2.7 artifact-level audit (I re-derive none of its 18 requirement rows; I cite them as prior work and extend to the other 14 units); W30's registry §2.6/§2.7 denominator-zero finding; the user-rejected registry ICD-O paper; W07f's Morioka retrieval. **W25 not read, not referenced.** No retrieval of any kind; the frozen corpus was not needed because every claim here is about the live checkout's committed bytes, and I record that I read `/home/user/Rare-cancers` at the two HEADs above.

**Overlap declared with W30b:** §5.1 F1 below generalises its F1 (6 generators absent from preflight's generator gate) to the whole policy (23 absent, 0 present). Different denominator, different sections.

## Method and inputs

**Requirement source:** `/home/user/Rare-cancers/systems/POLICY-evidence.md`, 386 lines, read in full. It contains **16 numbered requirement units**: §1.1, §1.2, §1.3; §2.1–§2.7; §3; §4.1, §4.2, and **two sections both numbered §4.3** (line 361 "Direction of bias", line 372 "Generalization"); §5.

**Enforcement sources read:**

| Path | What I read |
|---|---|
| `scripts/validate-registry.mjs` (170 l) | every check, lines 41–170, in full |
| `scripts/preflight.sh` (1,648 l) | the 18-row generator gate (lines 847–864), the fast-gate list, the tier flags (550–583, 962, 1199, 1352–1371) |
| `.github/workflows/tests.yml` | trigger and job shape (push to main, PR, dispatch; `gates` + `pytest` jobs) |
| `research/meta/meta-analysis.mjs` | pooling method and its §2.1(3) filter |
| 10 policy-citing test modules | test **names and docstrings only** — pytest is not installed |

**Artifacts spot-checked:** `research/data/emc-clinical-registry.json` (25 citations, 14 cohorts, 4 patients, 2 `evidenceQuestions`) and `research/meta/results.json`.

**Tools:** system `python3` (stdlib only), `git`, `grep`. **`python3 -c "import pytest"` → `ModuleNotFoundError: No module named 'pytest'`.** No suite was run and **no suite result is asserted anywhere below**.

## Result

### 5.1 Headline

**The §2.6/§2.7 gate hole W30b found is not local to those sections — it is the shape of the entire contract.** The whole of `POLICY-evidence.md`'s commit-loop enforcement is **one 170-line script**, `scripts/validate-registry.mjs`, running against **one file**, the clinical registry. Everything else that enforces a policy requirement is either a test in an **opt-in tier** or **does not exist**.

Three measured facts carry that claim:

1. **23 of 23** generators that cite `POLICY-evidence` and ship a `--check` are **absent** from preflight's 18-row generator gate. Zero are present. (W30b measured 6 for §2.6/§2.7; the full number across §2.1–§2.7 is 23, plus `km_digitize.py`, which has a `--check` but does not cite the policy string, for 24.)
2. **Neither pytest tier runs by default.** `RUN_TESTS=0` and `RUN_MODALITIES=0` at lines 550/576; both need `PREFLIGHT_TESTS=1`, `PREFLIGHT_MODALITIES=1` or `PREFLIGHT_FULL=1`. So **every** test named below — §2.1's inclusion-criterion guard, §2.2's Wilson known-values check, §2.4's anchor guard, §2.6's and §2.7's refusal guards — is opt-in for an ordinary commit. `tests.yml` runs all four directories on push and is the stated authority; that is **post-commit**, by design and recorded as such.
3. **`validate-registry.mjs` has no test anywhere in the tree.** `grep -rn "validate-registry" --include='test_*.py'` returns **0 test modules**. The single script carrying the contract into the commit loop has no mutation test proving any of its rules fire.

**Conformance is nevertheless clean.** Across the registry and the meta-analysis output I found **0 violations** on every decidable requirement (denominators in §5.3). What I found instead are **two places where the gate is weaker than the text it enforces**, and **six requirement units with no enforcement of any kind**.

### 5.2 The enforcement map — all 16 units

Tier key: **DEFAULT** = runs on a bare `./scripts/preflight.sh`; **OPT-IN** = needs `PREFLIGHT_TESTS/MODALITIES/FULL=1` (CI runs it on push); **NONE** = no gate, test or validator found.

| § | Requirement | Enforced by | Tier | Verdict |
|---|---|---|---|---|
| 1.1 | every datum points to a citation by id | `validate-registry.mjs` at **4 call sites** (patients :73, cohorts :85, positions :133, systemicEvidence :149) | DEFAULT | enforced |
| 1.2 | title, year, ≥1 of pmid\|pmcid\|doi, url | validator :55–58, all **ERROR** | DEFAULT | enforced |
| 1.2 | record the `license` | validator :59 — **WARN only, non-blocking** | DEFAULT (advisory) | weaker than text |
| 1.2/1.3 | `verified: true` only when the link was opened and confirmed | **nothing reads the field.** `grep '"verified"'` over `scripts/ research/ systems/` returns only unrelated `research_cycle` status strings | **NONE** | **zero enforcement** |
| 1.3 | secondary ⇒ `primaryRef` | validator :86–87, :134, :150 | DEFAULT | enforced |
| 1.3 | never invent an identifier for an unfetched primary | `research/manuscripts/lint_citations.py` — but its subject is **manuscript prose**, not the registry: it anchors printed identifiers to a fetch or the provenance ledger | DEFAULT, **different artifact class** | partial, off-target |
| 2.1(1) | confirmed EMC, molecular/histological | — | **NONE** | **zero enforcement** |
| 2.1(2) | explicit **integer** `{events, denom}`; never back-derive from a percentage | validator :96–99 checks `typeof … === "number"` and `events<=denom` — **not integer-ness, and presence not required**. Modality tests `test_a_percentage_only_cohort_cannot_contribute_counts`, `test_the_counts_carry_their_denominator_and_refuse_a_rate` | DEFAULT (weakened) + OPT-IN | **gate weaker than text**: `3.5` passes the validator |
| 2.1(3) | outcome ≠ inclusion criterion | implemented in `meta-analysis.mjs` :36 (`stage === "distant"` skips metastasis); tested by `test_a_cohort_whose_inclusion_criterion_is_the_outcome_is_dropped_even_when_it_has_counts` | **OPT-IN only** — and `meta-analysis.mjs` is run by **no gate, no test, no workflow** | not in commit loop |
| 2.2 | denominator-weighted pool, **Wilson** interval, heterogeneity as range | **no central implementation.** 19 `wilson` definitions in the tree (16 in non-test source), on two z constants (`1.96` ×10, `1.959963984540054` ×3). Per-module tests only (`test_wilson_matches_known_values_including_the_boundaries`) | OPT-IN, **no owner** | one-fact-many-places |
| 2.3 | no double-counting | validator :113–117 flags a pooled `populationKey`+`stratum` collision — **WARN, not ERROR**. **Across studies: nothing.** | DEFAULT (advisory) | **gate weaker than text** |
| 2.4 | time-anchored survival never merged | `fiveYearDSS` / `dssText` have **zero consumers** in the tree, so the prohibition is vacuous; guarded by `test_the_cross_cohort_comparison_refuses_to_run_across_anchors`, `test_nothing_is_pooled` | OPT-IN | enforced vacuously |
| 2.5 | stated limitations shown to the user via "the banner and methodology note" | the surface named is the **retired patient site** | **NONE** | requirement names a retired surface |
| 2.6 | study-level descriptive series (a)–(h) | **no gate** (W30b, reconfirmed); `test_endpoint_logic.py`, `test_endpoint_producers_check.py` | OPT-IN | as W30b found |
| 2.7 | reconstructed patient-level survival (a)–(f) | **no gate** (W30b); `test_emc_ipd_survival.py` | OPT-IN | as W30b found |
| 3 | contested ⇒ ≥2 opposing positions; name the mechanism of conflict; bottomLine states what is unproven | validator :124–141 — **the only consumer of `evidenceQuestions` in the entire tree**. Structure enforced; **`caveat` and `bottomLine` content: nothing** | DEFAULT (structure only) | **gate weaker than text**, see below |
| 4.1 | `studyPeriod` from what the source states; mark absent otherwise | validator `checkPeriod` :63–68 (shape, ERROR) + :90–91 (**presence on a pooled cohort: WARN only**) | DEFAULT (presence advisory) | partial |
| 4.2 | vintage surfaced everywhere; "diagnosed since" control | retired site surface | **NONE** | requirement names a retired surface |
| 4.3 (first) | direction of bias — conservative floor, never a silent upward adjustment | — (the three `conservative floor` hits are in `junction_aso_thermo.py` / decoy-null tests, unrelated) | **NONE** | **zero enforcement** |
| 4.3 (second) | generalization to every cancer page | — ; **and it duplicates the previous ordinal**, so §4 has two §4.3 and no §4.4 | **NONE** | **zero enforcement + numbering defect** |
| 5 | checklist when adding registry data | 6 of 7 boxes restate §1–§4; the 7th points at the validator | DEFAULT via the validator | derivative |

**Sections with literally zero enforcement: §1.2's `verified` semantics, §2.1(1), §2.5, §4.2, §4.3 (both), and §3's semantic half.** Sections whose real enforcement is entirely opt-in: **§2.1(3), §2.2, §2.4, §2.6, §2.7** — and `meta-analysis.mjs`, which implements §2.1(3) and is the manuscript's pooler, is run by nothing at all.

### 5.3 Conformance spot-checks — satisfy / violate / uneval, honest denominators

All rows `PRIMARY` as statements about repository state (I read the bytes and recomputed).

| # | Requirement | Sat | Viol | Uneval | Denominator | Evidence |
|---|---|---|---|---|---|---|
| C-1 | §1.2 hard requirements (title, year, resolvable id, url) | **25** | 0 | 0 | 25 citations | 0 missing on each of the four fields |
| C-2 | §1.2 `license` recorded | **25** | 0 | 0 | 25 | 0 missing |
| C-3 | §1.2/§1.3 `verified: true` means a link was opened and the claim confirmed | 0 | 0 | **25** | 25 (all assert `true`) | The field records a human/agent act performed outside the repository, no code reads it, and I retrieved nothing. **UNKNOWN, not a pass and not a fail.** |
| C-4 | §1.3 secondary ⇒ `primaryRef` | **3** | 0 | 0 | 3 secondary cohorts (11 primary) | 0 secondary cohorts lack `primaryRef` |
| C-5 | §2.1(2) explicit integer `{events, denom}`, events ≤ denom | **12** | 0 | 0 | 12 metric blocks over 14 cohorts | 0 non-integer cells, 0 `events>denom` — the registry satisfies the *text*, not merely the weaker gate |
| C-6 | §2.3 within-study: pooled strata disjoint | **5** | 0 | 0 | 5 pooled cohorts, all carrying a `populationKey` | 0 `(populationKey, stratum)` collisions |
| C-7 | §2.3 across-studies: overlapping series `pool:false` + `contextReason` | **9** | 0 | 0 | 9 context cohorts | every one carries a reason; 4 name `population-overlap`, 3 `percentage-only`, 2 `different-endpoint` |
| C-8 | §2.4 time-anchored survival not merged | **8** | 0 | 0 | 8 `dssText` + 2 `fiveYearDSS` fields | **zero consumers tree-wide**; nothing merges them |
| C-9 | §3 contested ⇒ ≥2 opposing positions | **1** | 0 | 0 | 1 contested question (of 2) | `rt-localized-emc`: 2 `supports` + 3 `against` — satisfies the policy text, not merely the validator's weaker branch |
| C-10 | §3 mechanism of conflict named per position; `bottomLine` present | **2** | 0 | 0 | 2 questions, 9 positions | 9/9 positions carry `caveat`; 2/2 carry `bottomLine`. **Unenforced by anything and nevertheless complete.** |
| C-11 | §4.1 `studyPeriod` present or explicitly marked absent | **5** | 0 | 0 | 5 pooled cohorts | 4 carry `studyPeriod`; the 5th (Meis-Kindblom) carries `studyPeriodUnknown: true` — the policy's own "mark it absent" path. 13 of 25 citations carry no `studyPeriod`, which the validator permits and §4.1 permits |
| C-12 | §2.1/§2.3 inputs to the manuscript pooler are current | **9** | 0 | 0 | 9 study rows across 3 metrics | I recomputed the pooler's study-level `(events, denom)` from the registry in Python, applying its own §2.1(3) `stage:distant` exclusion: **9/9 rows match `results.json` exactly**, and `k` matches on all three metrics (4 / 3 / 2). Nothing in the repository checks this |

**Totals: 12 requirement lines decided — 104 satisfying instances, 0 violations, 25 UNEVAL (C-3, the `verified` flag, at denominator 25).** Added to W30b's 16 satisfy / 0 violate / 2 uneval, the contract audits clean everywhere it has been looked at.

### 5.4 F1 — the generator gate, generalised

`scripts/preflight.sh`'s gate *"generated deposit artifacts reproduce from their generators"* (lines 847–864) enumerates 18 generators by path. Of the **23** generators in `research/manuscripts/`, `research/modalities/` and `scripts/` that cite `POLICY-evidence` **and** ship a `--check`, **0 are in the gate and 23 are absent**:

```
aso_coverage_ladder.py            emc_care_delivery_evidence.py     emc_recurrence_timing.py
aso_reagent_coverage.py           emc_fet_frame_and_composition.py  emc_rt_bed_reappraisal.py
emc_endpoint_alternatives.py      emc_ipd_survival.py               emc_scheduling_medians.py
emc_endpoint_discordance.py       emc_prognostic_coefficients.py    emc_site_curation.py
emc_fusion_partner_pooling.py     emc_radiotherapy_contradiction.py emc_surgical_quality.py
emc_systemic_therapy_pooling.py   hla_coverage.py                   km_risk_row_detect.py
endpoint_corpus.py  endpoint_regime_map.py  orr_dcr_reread.py  placebo_arm_calibration.py
nr4a3_tcip_reach.py
```

Method control: the same membership test returns 1 for `submission_tables.py` and `instrument_census.py`, which **are** gate rows — so the zeros are real absences, not a broken query. `km_digitize.py` is a 24th case: it has a `--check` but does not carry the policy string, so it fell outside this enumeration and inside W30b's.

This is the failure mode preflight's own comments record twice (`atr_hrd_sarcoma_series.py`, `instrument_census.py`): a `--check` that already exists and that nothing in the commit loop runs. The observation is about **coverage**, not a measured failure — I ran no generator this run and ran no preflight.

### 5.5 F2 — two places where the gate is weaker than the text it is cited as enforcing

Both are latent: **the registry does not exploit either**, so neither is a live defect.

1. **§2.1(2) integer-ness.** The policy says *"Explicit **integer** counts are reported… We never derive counts from a published percentage for pooling (rounding invents data)."* The validator's test is `typeof m.events !== "number"` (`validate-registry.mjs:98`). A back-derived `events: 3.5` — exactly the artifact of deriving a count from a percentage — passes gate 10 and reaches `meta-analysis.mjs`, which sums it. Measured: **0 of 12 metric blocks are non-integer today.**
2. **§3 "≥2 positions taking opposing stances (validator-enforced)".** The implementation is `if (!(stances.has("supports") && stances.has("against")) && !stances.has("mixed")) errors.push(...)` (`:139–140`). A question marked `contested` with **one** position of stance `"mixed"` satisfies it — the parenthetical "(validator-enforced)" over-describes the check by one position. Measured: the one contested question carries **5** positions on both sides.

A third, milder case: §2.3 is the policy's "cardinal sin", and its within-study guard is a **`warns.push`**, not an `errors.push` — a preflight run stays green with the warning on stdout. §4.1's presence check is likewise a warning.

### 5.6 F3 — the contract's own numbering, and two requirements whose surface is gone

§4 contains **two sections numbered 4.3** ("Direction of bias", line 361; "Generalization", line 372) and no §4.4. A cross-reference to "POLICY-evidence §4.3" is therefore ambiguous — the same defect class the file's own header banner records for the `METHODOLOGY.md` basename collision and for the gate ordinal that "had four homes and three of them said 2". No committed file cites §4.3, so nothing is currently mis-resolved. The tree cites §4 exactly **once** by number, at `review-seats/PUB-FUSION-PARTNER-…-round4-p1-rederivation.json` (§4.1).

Separately, §2.5's enforcement mechanism ("the banner and methodology note say all of this") and §4.2's ("a user-facing *diagnosed since (year)* control") name the **retired patient-facing site**. The requirements are unenforceable rather than unenforced, and the file's own banner says the contract survived the site while the framing did not. Recording it as an observation, not a defect: `CLAUDE.md` §7 forbids recreating the site.

### 5.7 F4 — the section nothing points at

`evidenceQuestions` — §3, the contested-evidence mechanism — has **exactly two references in the whole tree**, both inside `validate-registry.mjs`. No generator reads it, no manuscript quotes it, no view renders it, no test touches it. §3's "Link to the pool" clause (point the reader at the relevant `evidenceQuestions` entry when a pooled metric shows wide spread) therefore has **no implementation anywhere**, while `results.json` records `I2 = 90.4%` for recurrence and `69.1%` for metastasis — precisely the wide spread the clause is written about. This is a *wiring* observation about repository structure. **It is not a clinical claim: nothing here says radiotherapy or any other treatment works, is safe, or should be given.**

## Validation evidence

**RUN.** Environment: `/home/user/Rare-cancers`, HEAD `5ae0fa04` → `606d79f9`, system `python3` (stdlib only, **no third-party packages**), `git`, `grep`. Execution under `/tmp/claude-0/w30c/` (since deleted).

```
$ python3 -c "import pytest"
ModuleNotFoundError: No module named 'pytest'

$ grep -rn "governed_by" --include='*.json' --include='*.py' --include='*.mjs' --include='*.md' .
   → 9 non-report hits, all "systems/POLICY-evidence.md 2.6"; 0 naming 2.7

$ grep -rn "evidenceQuestions" --include='*.py' --include='*.mjs' --include='*.js' .
   scripts/validate-registry.mjs:124
   scripts/validate-registry.mjs:125          (2 hits, 1 file)

$ grep -rn "validate-registry" --include='test_*.py' .
   (no test module)

$ grep -rn -E "^\s*def _?wilson[0-9]*\(|^\s*(function|const) wilson" --include='*.py' --include='*.mjs' --include='*.js' . | wc -l
   19          # 16 outside tests/;  z=1.96 ×10, z=1.959963984540054 ×3
```

Registry enumeration (stdin heredoc, verbatim):

```
citations: 25
verified: Counter({True: 25})
license missing: 0
no resolvable id: 0
no studyPeriod: 13
cohorts: 14
pool true: 5
provenance: Counter({'primary': 11, 'secondary': 3})
patients: 4
evidenceQuestions: 2
   rt-localized-emc contested ['supports','supports','against','against','against'] True 5
   adjuvant-chemo-localized-emc consensus-against ['against','against','against','against'] True 4

metric blocks: 12 non-integer: 0 events>denom: 0
pool:false contextReasons: {'population-overlap (US single institution; likely within SEER /
  US Sarcoma Collaborative)': 1, 'population-overlap; percentage-only': 2, 'percentage-only': 3,
  'different-endpoint': 2, 'population-overlap': 1}
pooled cohorts lacking studyPeriod: [(2, 'Long-term outcome series (Meis-Kindblom)', True)]
pooled popKey+stratum dups: []
pooled cohorts with populationKey: 5 of 5
secondary missing primaryRef: []
```

Independent recomputation of the pooler's inputs (stdin heredoc, verbatim):

```
results.json study rows checked: 9, mismatches vs registry recomputation: 0
k per metric: {'recurrence': 4, 'metastasis': 3, 'diseaseDeath': 2}
   recomputed: {'recurrence': 4, 'metastasis': 3, 'diseaseDeath': 2}
```

Generator-gate membership, with its control:

```
$ (for each of 23 policy-citing generators shipping --check) grep -c "$f" scripts/preflight.sh
   → 0 for all 23
$ grep -c "research/manuscripts/submission_tables.py" scripts/preflight.sh    → 1
$ grep -c "research/modalities/instrument_census.py"  scripts/preflight.sh    → 1
```

Read-integrity across the HEAD move:

```
$ git diff --stat 5ae0fa04ff9516ac8f820381079d644a094f4a77 606d79f96526b651f3b825190d721f6b302c032e \
    -- systems/POLICY-evidence.md scripts/validate-registry.mjs scripts/preflight.sh \
       research/data/emc-clinical-registry.json research/meta/meta-analysis.mjs research/meta/results.json
(empty)
diff-exit=0
```

**PROPOSED (NOT RUN).** The ten test modules that cite `POLICY-evidence` — `research/modalities/tests/{test_emc_site_curation,test_emc_radiotherapy_contradiction,test_emc_recurrence_timing,test_locoregional_eligibility}.py`, `research/manuscripts/tests/{test_fusion_partner_prose_matches_its_artifact,test_endpoint_logic,test_aso_coverage_ladder,test_emc_fusion_partner_pooling_check,test_emc_systemic_therapy_pooling_check}.py`, `systems/tests/test_systems_check.py`. **pytest is not installed in this container, so I ran none of them and assert no pass or fail for any.** A skipped test is not a pass. My statements about them are limited to test *names* I read directly. I did not run `research/manuscripts/tests/test_endpoint_producers_check.py` and would not have with pytest present: it perturbs committed artifacts on disk.

## Limitations

1. **`grep` finds citation, not enforcement.** A gate could enforce a policy requirement without naming the policy, and my map would miss it. I mitigated this by reading `validate-registry.mjs` in full, reading the gate list and tier flags in `preflight.sh` directly, and enumerating `evidenceQuestions`/`verified` consumers by field name rather than by policy reference — but "NONE" in the table means **I found none**, which is UNKNOWN rather than proven absence.
2. **No test result of any kind.** pytest is absent. The OPT-IN tier's tests may pass, fail or error; I do not know and do not assert. What I establish about them is *where they run*, which is read off the script.
3. **The conformance denominators are small.** 25 citations, 14 cohorts, 2 evidence questions, 9 pooled study rows. A clean audit at n=14 is a clean audit at n=14.
4. **C-3 is unresolvable here.** `verified: true` records an act performed outside the repository. I retrieved nothing and opened no source, so 25 of 25 stay UNKNOWN. The fact that no code reads the field makes it undecidable *from the repository* as well, which is the finding.
5. **Commit ordering is undecidable.** The registry and `results.json` are both squashed to `14a3f172`, so I cannot establish that `results.json` was regenerated *after* any given registry edit — only that it is consistent with the registry **now**, which I measured.
6. **Two units of the contract describe a surface that no longer exists** (§2.5's banner, §4.2's control). I record them as unenforceable, and I do not propose reviving the retired site.
7. **No clinical claim.** A policy-conformance result says nothing about whether any treatment works, is safe, selective, or ready for a patient. The `I2` values in §5.7 are quoted as evidence that a *wiring* clause has no implementation, not as evidence about radiotherapy or any other therapy. There is no wet lab.

## Stop condition

**Set up front:** enumerate every numbered requirement unit of `POLICY-evidence.md`; for each, identify the committed artifacts it governs and whether any gate, test or validator enforces it and in which tier; name the units with zero enforcement and those whose enforcement is opt-in; spot-check conformance with an honest denominator, prioritising breadth over depth since W30b did depth on two — then return.

**MET.** All **16** units are mapped. **6 have zero enforcement of any kind**; **5 more are enforced only in an opt-in tier**; the commit-loop enforcement of the whole contract is one 170-line script, itself untested. Conformance spot-checks across 12 requirement lines give **104 satisfy, 0 violate, 25 UNEVAL** on stated denominators, plus two latent gate-vs-text divergences that the governed artifacts do not exploit.

## Tool-call and wall-clock count actually used

**22 tool calls** (20 Bash, 2 Read), of which 2 were the mandated start/end state records. **0** network calls, **0** retrieval calls, **0** generator invocations, **0** repository writes, **0** git write operations. Wall clock **03:41:55Z → 03:45:44Z ≈ 3.8 minutes** of measured tool time, plus report drafting. Well inside the ~40/~40 target; returning now rather than padding.

## Next concrete action

**The successor task for this lane is a one-file, one-question audit that no worker has done: read `scripts/validate-registry.mjs` against the twelve registry-facing sentences of `POLICY-evidence.md` and produce the divergence list in full.** I found two divergences (§2.1(2) integer-ness, §3's "≥2 positions") plus two error-vs-warning choices (§2.3, §4.1) while reading for a different purpose, on the one script that is the entire commit-loop enforcement of the contract and that **has no test of its own**. A systematic pass would settle whether those four are the whole list. It needs no science, no network and no writes to produce the finding — and the repair, if the user wants one, is then a choice per divergence between tightening the check and softening the policy's "(validator-enforced)" parenthetical, which is a decision for the owner, not for a worker.

I propose this; **I have written nothing, authored no repair, added no gate row and changed no tier budget.** W30b's two proposals (add the generators to the gate; make `pool_reconstructions` raise on overlap) stand unaddressed by me and are now known to be the narrow case of the 23-generator absence in §5.4.
