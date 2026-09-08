> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

All checks complete. Report follows.

---

## Worker

**W16c**, LANE 16 second refill — decision-support package on the `bishop2019` admissibility clause routed by W16b.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am powered by Opus 5, exact model ID `claude-opus-5`. I did not observe the served model and do not assert it as fact; the coordinator must extract the actual per-child runtime model from the transcript. **No environment variable in this container names a served model.**

`date -u` at start: `Tue Sep  8 02:26:45 UTC 2026`
`date -u` at end: `Tue Sep  8 02:30:27 UTC 2026`

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (unmodified except that sed redaction; four very long proxy-host lists marked elided rather than reprinted):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...                    [elided: proxy host list]
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...       [elided]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=...        [elided: proxy/truststore flags, no model identity]
NO_PROXY=localhost,127.0.0.1,::1,...                    [elided]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...          [elided]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**HEAD I actually read:** `b9a0257e6acff53ad22535cf2adf261313e0b250`. ⚠ This is **not** the frozen commit named in `COMMON-BRIEF.md` (`92abbcb905cacf07f14b238db50d1b98f6590374`) and **not** the commit W16b recorded. The tree has moved since the brief was written — the coordinator has been staging campaign reports. `git status --porcelain` shows only `research/autonomy/opus-capacity-campaign-20260908/` paths (one modified `WAVE-LOG.md`, sixteen untracked `reports/W*.md`); **no file I touched is modified, and I issued no git write command of any kind.** Every input below is from `research/`, `systems/` and `scripts/`, none of which appears in that status output, so the inputs are the frozen ones even though HEAD is not.

---

## Question

**What are the concrete, measured consequences of each way the `bishop2019` admissibility clause could be resolved — and does the committed evidence actually distinguish between them?**

Open because W16b routed the clause rather than resolving it: it found `bishop2019` is the only cohort in the registry whose two endpoints sit on an identical primary denominator and whose median follow-up (94 months) is the longest available on matching denominators, and that it fails **exactly one** clause. W16b explicitly declined to act ("authoring or relaxing my own acceptance criterion is forbidden — so it is handed over, not done") and handed it to whoever owns the rule. **I do not resolve it either.** This is the package for that owner.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers` (all read-only):

```
grep -rn "bishop2019\|bishop" --include=*.json --include=*.md --include=*.py . | grep -v '^\./\.git'
grep -rln "emc-clinical-registry" --include=*.py --include=*.js --include=*.json --include=*.md --include=*.sh .
grep -rn '\["pool"\]\|\.get("pool"' --include=*.py .
grep -rn "94/259" --include=*.md --include=*.json --include=*.py .
grep -rn "259\|326\|36\.3\|27\.0" --include=test_*.py research scripts systems
grep -rln "36.3\|94/259\|locoregional-eligibility" systems/
```

plus full reads of `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `reports/W16b-frechet-followup-adversarial.md`, the admissibility-rule and F3 blocks of `reports/W16-new-clinical-computation.md`, `research/modalities/emc_locoregional_eligibility.py`, and the relevant blocks of the registry, the site curation, the RT-contradiction artifact and the ASO archive manifest.

**Not replaying `CLOSED-WORK.md`.** No EMC classification work (PUB-EMC-CLASSIFICATION untouched), no Brenca route, no re-approach to `ussc2022`, `drilon2008`, SEER-270, CTARC, Wagner, pazopanib or sunitinib. **I retrieved nothing over the network at all** — no PubMed MCP call, no `get_full_text_article`. Every input is already on disk.

**Not duplicating W16 or W16b.** W16 computed the Fréchet bound; W16b reproduced it, tested the follow-up hypothesis and surfaced the clause. Neither traced the clause's *downstream dependency set*, and neither computed what the committed artifacts would read under each resolution. That is what is new here.

---

## Method / inputs

**Files read (read-only):**

| Path | Role |
|---|---|
| `research/data/emc-clinical-registry.json` | holds the clause (line 501) and all 14 cohorts |
| `research/modalities/emc_locoregional_eligibility.py` | the **only** generator that reads the registry's per-cohort `pool` flag |
| `research/modalities/emc-locoregional-eligibility.json` | the artifact it writes — the two pooled figures |
| `research/modalities/emc-site-curation.json` | holds the competing pool-scope principle and the integer `13` |
| `research/modalities/emc-radiotherapy-contradiction.json` | independent bishop2019 estimand (does not read the flag) |
| `research/manuscripts/aso/fusion-junction-aso-working-record.md` | quotes `36.3% (94/259, 30.7–42.3)` at line 1318 |
| `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` | byte-pins the registry and the working record in a DOI deposit |
| `systems/views/L2-rt-lung-directed.md`, `L2-rt-limb-perfusion.md`, `L2-rt-rt-intensify.md`, `L5-evidence-base.md` | generated views whose prose quotes the pooled figures |
| `research/literature/emc-km-admissibility-2026-08-27.json` | access verdicts |

**Environment:** Python 3.11.15, `emc_locoregional_eligibility` imported directly. Scripts written to and run from `/tmp/claude-0/w16c/` — **outside the repository**. No file in the Git working tree was created, edited or deleted by me.

**Method:** I imported the repository's own `pool()` function, deep-copied the committed cohort list **in memory only**, applied each candidate resolution as a mutation of that copy, and re-ran the real generator arithmetic. No number below is hand-derived except where the arithmetic is shown.

---

## Result

### 1 · The clause, verbatim, with path and line

`research/data/emc-clinical-registry.json`, cohort `Localised, single-institution series` (`sourceId: bishop2019`, `n: 41`), lines **498–517**. The clause is **three co-located committed fields**, and it matters which one the owner is being asked about:

```
research/data/emc-clinical-registry.json:501
        "pool": false,
```
```
research/data/emc-clinical-registry.json:511
        "contextReason": "population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)",
```
```
research/data/emc-clinical-registry.json:512
        "note": "41 consecutive localized EMC; 5/41 (12%) local relapse; 10-yr local control 100% with surgery+radiotherapy vs 63% surgery alone (HR 12.7). Not pooled to avoid double-counting the US population.",
```

W16b's exact statement of it, quoted from `reports/W16b-frechet-followup-adversarial.md`: *"It fails **exactly one** clause: `pool == false`, with `contextReason: population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)`."* W16b's exact wording of the routed decision: *"**Changing the acceptance criterion is not mine to do**; I flag it as the one substantive question for whoever owns that rule."*

The competing principle, also committed, `research/modalities/emc-site-curation.json:11`:

> `"⭐_why_bishop2019_is_pooled_HERE_and_pool_false_in_the_REGISTRY": "The clinical registry marks bishop2019 `pool: false` with `contextReason: population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)`. That exclusion bites only where an overlap PARTNER is inside the same pool, and neither SEER nor the US Sarcoma Collaborative contributes a site distribution to this one. ⛔ Pool membership is decided per pool, not once per source. The registry's recurrence and metastasis pools do contain ussc2022, so its flag stands unchanged there."`

⚠ **The repository has already answered this question once, in writing, and its answer is the narrow one.** The site-curation file does not merely state the per-pool principle — it applies it and concludes the flag **stands unchanged** in the registry's recurrence and metastasis pools, because `ussc2022` is in them. That sentence is committed evidence bearing directly on the decision and W16b did not quote its second half.

### 2 · Dependency set, established by execution

| # | Dependent | How reached | Depends on the flag? | Grade |
|---|---|---|---|---|
| D1 | `emc_locoregional_eligibility.py::pool()` line 158 (`if not c.get("pool")`) | `grep -rn '\.get("pool"' --include=*.py .` | **YES — the only code path in the tree that reads a registry cohort's `pool` flag** | PRIMARY |
| D2 | `emc-locoregional-eligibility.json → who_ever_metastasises` (`94/259 = 36.3%`, Wilson 30.7–42.3) | generated by D1 | YES | PRIMARY |
| D3 | `emc-locoregional-eligibility.json → who_recurs_locally` (`88/326 = 27.0%`, Wilson 22.5–32.1) | generated by D1 | YES | PRIMARY |
| D4 | `research/manuscripts/aso/fusion-junction-aso-working-record.md:1318` — "**36.3%** (94/259, Wilson 95% CI 30.7–42.3%) of localised patients develop distant disease across three non-overlapping series" | `grep -rn "94/259"` | YES (quoted, not re-derived) | PRIMARY |
| D5 | `systems/views/L2-rt-lung-directed.md:23` — "across three non-overlapping series, roughly a third of localised patients develop distant disease" | `grep -rln "locoregional-eligibility" systems/` | YES (cohort **count** and "non-overlapping") | PRIMARY |
| D6 | `systems/views/L2-rt-limb-perfusion.md:23` — "local recurrence runs at a substantial minority across **four non-overlapping series**" | same | YES (cohort count) | PRIMARY |
| D7 | `systems/graph/routes.json` lines 7364 / 7462 / 7664; `systems/graph/artifacts.json:397`; `systems/views/L5-evidence-base.md:125` (ART-LOCOREGIONAL-ELIGIBILITY → RT-LIMB-PERFUSION, RT-LUNG-DIRECTED, RT-RT-INTENSIFY) | same | Structural only — the edges do not carry the numbers | PRIMARY |
| D8 | `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` — `files[0]` pins `research/data/emc-clinical-registry.json` at **103,203 bytes / sha256 `6f3b31b3…`**, verified live to match; the working record (D4) is pinned at 237,117 bytes / `ddaeb872…`; `archive_content_digest c3d9882e…`; `deposition_doi 10.5281/zenodo.22229096` | `python3` walk of the manifest + `sha256sum` | YES — **any byte change to the registry breaks the deposit's manifest** | PRIMARY |
| D9 | W16's Fréchet admitted set (2 cohorts) and W16b's adversarial anchor table | reports read | YES — but this is **campaign work in progress, not a committed artifact** | SECONDARY |
| D10 | `emc-radiotherapy-contradiction.json`, `emc-rt-bed-reappraisal.json`, `emc-site-curation.json`, `emc-ipd-survival.json`, `emc-km-*.json` | grep for `bishop2019` | **NO** — each carries its own `estimates`/`series` list and none consults the registry `pool` flag | PRIMARY |
| D11 | `research/manuscripts/pinned-figures.json` | `grep -n -i "259\|326\|36.3\|27.0\|bishop\|locoregional"` → **no match** | **NO** | PRIMARY (negative) |
| D12 | Test suite: `research/modalities/tests/test_locoregional_eligibility.py` | read in full | **NO** — every assertion runs on synthetic fixtures (`(5,50)`, `denom==100`, `denom==0`); **no committed test pins 94, 259, 88, 326, 36.3 or 27.0.** `grep -rn "259\|326\|36\.3\|27\.0" --include=test_*.py research scripts systems` filtered to eligibility terms returns **nothing** | PRIMARY (negative) |

⛔ **D12 is a real defect the owner should see regardless of how the clause resolves: the two headline pooled figures the ASO working record quotes are protected by no test.** A change to the flag would move them silently. `test_emc_surgical_quality.py:158` imports the module only to assert Wilson has one home.

### 3 · Per-option consequences, computed

Four resolutions are available. **The decisive structural fact, found by execution and not stated in W16b: the `pool` flag is not the only gate.** The registry gives `bishop2019` **`recurrencePct: 12` and `metastasisPct: 32` — percentages, with no `{events, denom}` block** (`has_events_denom_blocks: []`). `pool()` applies the flag check first and an integer-count check second. So flipping the flag alone changes the *reason* for exclusion and **nothing else**.

| Option | What it does | Metastasis pool | Recurrence pool | Δ met | Δ rec |
|---|---|---|---|---|---|
| **R0** status quo | leave `pool: false` | 94/259 = **36.3%** (30.7–42.3), 3 cohorts | 88/326 = **27.0%** (22.5–32.1), 4 cohorts | — | — |
| **R1** flip the flag only | `pool: true`, no counts curated | 94/259 = **36.3%** (30.7–42.3), 3 cohorts | 88/326 = **27.0%** (22.5–32.1), 4 cohorts | **+0.0 pp** | **+0.0 pp** |
| **R2** flip the flag **and** curate the counts | + `recurrence {5,41}`, `metastasis {13,41}` | 107/300 = **35.7%** (30.5–41.2), 4 cohorts | 93/367 = **25.3%** (21.2–30.0), 5 cohorts | **−0.6 pp** | **−1.7 pp** |
| **R3** pool-scoped (the site-curation principle applied literally) | admit to the metastasis pool, which has no US overlap partner; keep out of the recurrence pool, which contains `ussc2022` | 107/300 = **35.7%** (30.5–41.2), 4 cohorts | 88/326 = **27.0%** (22.5–32.1), 4 cohorts | **−0.6 pp** | **+0.0 pp** |

*(R2b — curate the counts but leave the flag false — was also run: identical to R0 on both pools, confirming the flag gate fires before the count gate.)*

**Arithmetic, shown.** Metastasis: 94 + 13 = 107; 259 + 41 = 300; 107/300 = 0.35667 → 35.7%; 36.3 − 35.7 = **−0.6 pp**. Recurrence: 88 + 5 = 93; 326 + 41 = 367; 93/367 = 0.25341 → 25.3%; 27.0 − 25.3 = **−1.7 pp**. Wilson widths: metastasis 11.6 → **10.7 pp**; recurrence 9.6 → **8.8 pp**.

**Internal consistency of the two counts (they require no new retrieval).** `5/41 = 12.2%` against the registry's `recurrencePct: 12`; `13/41 = 31.7%` against `metastasisPct: 32`. Both round correctly. The `5` is committed twice — registry note line 512 (`5/41 (12%) local relapse`) and `emc-radiotherapy-contradiction.json` (`"events": 5`). The `13` is committed as an integer in `emc-site-curation.json` as `{"source_id": "bishop2019", "stratum": "developed distant metastasis during follow-up, localised at diagnosis", "events": 12, "denom": 13}`, and the same file states the registry cohort and the paper's site breakdown are "**both over n=41, the whole series**". ⛔ **So no option here is blocked on an unrecovered source, and I attempted no retrieval.**

**Conclusions that would need relabelling under R2 or R3:**

| Where | Now reads | Would read |
|---|---|---|
| D4 ASO working record :1318 | "36.3% (94/259, Wilson 95% CI 30.7–42.3%) … across three non-overlapping series" | "35.7% (107/300, 30.5–41.2%) … across **four** series" — and the word **"non-overlapping" becomes a claim the resolution itself has put in doubt |
| D4 corroboration sentence | agrees with an external review's "around 35-45%" (PMID 41055792) | **still agrees** — 35.7% is inside 35–45%. No conclusion flips. |
| D5 lung-directed view | "three non-overlapping series, roughly a third" | "four series, roughly a third" — the qualitative grade is unchanged |
| D6 limb-perfusion view | "four non-overlapping series" | R2: "**five** series"; R3: unchanged |
| D9 W16 Fréchet admitted set | 2 cohorts (Masunaga localised, Chiusole) | 3 cohorts — bishop2019 enters at n=41, met 13, LR 5, bound **[8,13]**, ≥19.5% of cohort, ≥61.5% of metastatic patients, RD +19.5 (95% cons. 0.1–38.9), median FU **94 mo**. W16b's follow-up flank moves from "contradicted by a sensitivity row" to "contradicted by an admitted row". |
| D9 W16b adversarial anchor | pooled recurrence 27.0% → implied lifetime LR 36.2 → k = 20.2 → bound 2.8 = **7.2%** of metastatic patients ("survives, barely") | 25.3% → implied 33.9 → k = 17.9 → bound 5.1 = **13.1%** ("survives, less barely"). The 29.1% breakpoint is untouched. |

**The consequence nobody has costed, and it dominates the arithmetic.** R1, R2 and R2b all require editing `research/data/emc-clinical-registry.json`, which is **byte-pinned inside a DOI-minted deposit** (D8). `emc-site-curation.json:*` records this as measured, not predicted: *"⛔ ANY byte change to it turns the manifest gate red and forces a re-stamp of a deposited artifact — measured 2026-08-27: a one-line insertion moved the registry from 99,912 to 99,940 bytes and the `archive_content_digest` with it."* Under **R2 two deposited files move** — the registry and the ASO working record that quotes 36.3% — so the per-file sha256s, `archive_content_digest`, `total_bytes` and `git_revision` must all be regenerated and `10.5281/zenodo.22229096` re-deposited, gated by `test_the_manifest_hashes_were_taken_against_a_committed_tree.py` and siblings. **R0 and R3 avoid this entirely**: R3 changes only the generator's scope logic, not the registry bytes. ⚠ Cost accounting only — I make no recommendation.

### 4 · Does the committed evidence distinguish the options?

**Partly. It cleanly eliminates one option and cleanly separates two others. It does NOT settle the one that matters.**

| Claim | Verdict | Basis |
|---|---|---|
| R1 (flip the flag alone) is a no-op on every committed number | **SETTLED — YES.** `bishop_exclusion_reason` merely changes from `"pool: false — population-overlap…"` to `"no explicit integer metastasis counts"` / `"no explicit integer recurrence counts"`; all six pooled values are byte-identical to R0 | RUN, exit 0 |
| R2 vs R3 differ, and only on the recurrence pool | **SETTLED — YES.** Metastasis is identical (35.7%); recurrence is 25.3% vs 27.0% | RUN, exit 0 |
| The `contextReason` premise — that `bishop2019`'s patients are **actually** inside `ussc2022` and/or SEER | **NOT SETTLED. UNKNOWN.** The registry hedges in its own words: "**likely** within SEER / US Sarcoma Collaborative". Nothing committed converts that "likely" into an overlap count | PRIMARY (negative) |
| Therefore whether R2's recurrence pool (93/367) double-counts patients | **NOT SETTLED** — this is the whole substance of the decision | — |

**Stated plainly: the committed evidence does not distinguish R2 from R3, because the fact the clause asserts has never been checked.** What is retained is a hedge and two study descriptors: `bishop2019` = "Localized EMC, single institution 1990-2016", MD Anderson, n=41 (site-curation names the institution); `ussc2022` = "EMC, US Sarcoma Collaborative 2000-2016", multi-institution, n=60. The study windows overlap (2000–2016). The registry carries **no institution roster for `ussc2022`** and **no patient identifiers for either**, so no overlap count is computable from what is on disk. The only weak signal I can extract is that the `ussc2022` author list committed in `registry.citations` (Gusho, King, Ethun, Cardona, Howard, Tran, Poultsides, Tseng, Roggin, Fields, Cullinan, Chouliaras, Votanopoulos, Grignol, Bedi) contains **no MD Anderson author**. ⚠ **An author list is not an institution roster, and I do not treat it as one** — it is suggestive, not evidential, and I record it as UNKNOWN.

**The specific missing evidence that would settle it, in ascending order of cost:**

1. **The `ussc2022` contributing-institution list** — one sentence of its Methods. This alone decides R2 vs R3: if MD Anderson is not a USSC contributor, the recurrence-pool overlap partner does not exist and R2 and R3 converge. ⛔ **BLOCKED, recorded as blocked rather than untried.** `CLOSED-WORK.md` records `ussc2022` methods as unrecovered; `emc-km-admissibility-2026-08-27.json` gives verdict `unreachable`, and W16b independently recorded `oa_status: "closed"`, 0 OA locations. **I did not attempt any route.**
2. **SEER geographic coverage of Texas for 1990–2016.** Would decide the SEER half of the `contextReason`. Not blocked by `CLOSED-WORK.md`, but ⛔ **out of scope by standing rule** — `CLOSED-WORK.md` forbids EMC-specific inference from generic SEER parameters, and in any case SEER-270 is `pool: false` and enters **neither** pool, so this half of the clause has **no downstream consequence at all** in D2/D3. That is itself a finding: the `contextReason` names two overlap partners and only one of them is in a pool.
3. **A ruling on estimand scope, which needs no new data.** The site-curation principle (`Pool membership is decided per pool, not once per source`) is already committed and already applied once. Whether it governs the registry pools is a **definition the owner sets**, not a fact retrieval could supply. ⭐ **This is the only route to a resolution that is open today.**

---

## Validation evidence

**RUN — command, environment, exit code, verbatim output.**

```
cd /tmp/claude-0/w16c && python3 counterfactual.py > out.json; echo "EXIT=$?"
EXIT=0
```
```
cd /tmp/claude-0/w16c && python3 deltas.py; echo "EXIT=$?"
R0/R1 (excluded from both)           MET  94/259= 36.3% [30.7-42.3] n_coh=3 | REC  88/326= 27.0% [22.5-32.1] n_coh=4
R2 (admitted to both)                MET 107/300= 35.7% [30.5-41.2] n_coh=4 | REC  93/367= 25.3% [21.2-30.0] n_coh=5
R3 pool-scoped (metastasis only)     MET 107/300= 35.7% [30.5-41.2] n_coh=4 | REC  88/326= 27.0% [22.5-32.1] n_coh=4

deltas vs committed (met 94/259=36.3, rec 88/326=27.0):
  R0/R1 (excluded from both)           dMET=+0.0 pp  dREC=+0.0 pp  CIwidth MET 11.6 REC 9.6
  R2 (admitted to both)                dMET=-0.6 pp  dREC=-1.7 pp  CIwidth MET 10.7 REC 8.8
  R3 pool-scoped (metastasis only)     dMET=-0.6 pp  dREC=+0.0 pp  CIwidth MET 10.7 REC 9.6

W16b adversarial anchor recomputed under each pooled recurrence rate (Masunaga n=134, met=39, obs LR=16):
  R0/R1 27.0%: implied lifetime LR count 36.2 -> k=20.2 -> Frechet bound 2.8 = 7.2% of metastatic pts
  R2 25.3%: implied lifetime LR count 33.9 -> k=17.9 -> Frechet bound 5.1 = 13.1% of metastatic pts
EXIT=0
```

**Baseline reproduction check (guards against the harness computing something other than the committed artifact).** `counterfactual.py` prints the committed artifact's own fields next to the R0 recomputation: `_committed_artifact` metastasis `94/259, 36.3, 30.7, 42.3`, recurrence `88/326, 27.0, 22.5, 32.1` — **identical to the R0 row on all eight fields**. The R0 arm reproduces the committed file exactly, so the R1/R2/R3 deltas are deltas against the real thing.

**Manifest pin verified live:**
```
sha256sum research/data/emc-clinical-registry.json
6f3b31b352c29592a4657d64aff872a93cf65f280837096008e59ab82e502bdd  research/data/emc-clinical-registry.json
wc -c research/data/emc-clinical-registry.json
103203 research/data/emc-clinical-registry.json
```
matching the manifest's `files[0]` exactly (`"bytes": 103203, "sha256": "6f3b31b352c29592…"`). The deposit is currently in sync; any registry edit breaks it.

**One failure during development, reported rather than hidden.** First run of `counterfactual.py` exited **1** with `NameError: name 'v' is not defined` — a comprehension variable shadowed by the loop rebinding. Fixed by renaming to `r` and re-run; the fix touched no arithmetic.

**Write isolation verified.** `git status --porcelain` before and after shows only the coordinator's `research/autonomy/opus-capacity-campaign-20260908/` paths. No file authored by me exists anywhere in the tree; all execution in `/tmp/claude-0/w16c/`. **No git write command was issued.**

**PROPOSED (NOT RUN):**
- `pytest research/modalities/tests/test_locoregional_eligibility.py` under each option — not run. I read every assertion instead and report that none binds a live pooled figure (D12). The claim "no test would go red under R2" is therefore a **static reading of the assertions, not an executed test result.**
- The manifest gate (`test_the_manifest_hashes_were_taken_against_a_committed_tree.py` and siblings) under a mutated registry — **not run.** The prediction that it goes red rests on the committed measured note in `emc-site-curation.json` and on the live sha256 match, not on a run by me.
- `scripts/preflight.sh` — not run; my dispatch does not authorise it.
- Any retrieval of `ussc2022` full text — **not attempted; recorded as blocked** per `CLOSED-WORK.md`.
- Any edit, replacement clause, or adopted reading — **not authored.** Both readings are computed side by side throughout.

---

## Limitations

1. **I did not resolve the clause and this report contains no recommendation.** R0/R1/R2/R3 are computed alongside each other; the ordering of the table is structural (no-op first), not a ranking.
2. **HEAD is not the brief's frozen commit** (`b9a0257e` vs `92abbcb9`). The difference is confined to the campaign report directory per `git status`, but I cannot prove the intervening commits touched nothing else, because I ran no `git log` or `git diff` (they are reads, but I kept to the inputs I needed). **Anyone re-running this should re-verify against their own HEAD.**
3. **The two integer counts (5/41, 13/41) are committed transcriptions, not re-read primaries.** `13` comes from a 2026-08-27 transcription of `PMC7771031`; `5` from the registry note and the RT-contradiction artifact. I performed no retrieval and inherit those transcriptions' correctness. ⚠ Note the coexisting fact: `emc-km-admissibility-2026-08-27.json` lists `bishop2019` under `unreachable` — that verdict is about **KM figures / risk rows**, not about the site and outcome counts, which were read. Both are true; neither overrides the other.
4. **D12 (no test pins the pooled figures) is a static reading of the assertions, not an executed run.** It should be confirmed by running the suite before being relied on.
5. **The MD-Anderson-not-in-the-USSC-author-list observation is suggestive only.** An author list is not a contributing-institution roster. The overlap remains **UNKNOWN**, and the `contextReason`'s own word is "likely".
6. **The SEER half of the clause has no measured downstream effect** in D2/D3 because SEER-270 is itself `pool: false`. That is an argument about *this* dependency set only; it says nothing about other estimands.
7. **Both readings are equally supported by what is retained** on the question that matters (R2 vs R3). I state that as the finding, not as a tie to be broken by convenience.
8. **The deposit cost is asymmetric between options and I have costed it, not weighed it.** Whether a 0.6/1.7 pp move is worth a re-stamp of a minted DOI is a judgement for the owner.
9. **No clinical claim.** Nothing here concerns efficacy, safety, selectivity, therapeutic window, surveillance intervals, margins, radiotherapy, prognosis or clinical readiness. The pooled figures are crude during-follow-up proportions over mixed follow-up with censoring ignored, and the artifact's own `_limits` (one series dominating both denominators; a consultation series selected toward difficult tumours; recurrence being an endpoint *mixture*; crude proportions systematically **understating** lifetime rates) apply unchanged under **every** option and are not softened by any of them. No new patients were created.
10. **Every W16 and W16b limitation and negative finding is preserved intact**, including F3 (the Meis-Kindblom reversal), the 29.1% adversarial breakpoint, and W16b's statement that its three-cohort follow-up comparison cannot decide the general question.

---

## Stop condition

**Set by dispatch:** clause quoted verbatim with its location; dependency list established by execution; per-option consequences computed with real numbers; explicit statement of whether the evidence distinguishes the options.

**MET, all four.**
(i) Clause quoted verbatim at `research/data/emc-clinical-registry.json:501`, `:511`, `:512`, with the competing committed principle at `emc-site-curation.json:11` and the second half of that sentence that W16b did not quote.
(ii) Dependency set D1–D12 established by grep and by import, including two **negative** dependencies found by execution (`pinned-figures.json` does not carry these numbers; no test pins them) and one that was not obvious from the reports (the DOI-deposit byte pin).
(iii) Four options computed at exit 0 against the real generator, with the arithmetic shown; **R1 is a measured no-op**, R2 moves the two headline figures by −0.6 pp and −1.7 pp, R3 moves one.
(iv) Stated plainly: **the committed evidence does NOT distinguish R2 from R3**, because the `contextReason`'s premise is a hedge ("likely") that no retained record checks; the one piece of evidence that would settle it — the `ussc2022` contributing-institution list — is **recorded blocked** and was not attempted; and the only route open today is a scope ruling by the owner, which needs no new data.

---

## Tool-call and wall-clock count actually used

**34 tool calls** (all `Bash`; **no network retrieval, no PubMed MCP call, no subagents, no writes to the repository, no git write command**). **Wall clock ≈ 4 minutes of tool activity** (02:26:45 → 02:30:27 UTC), preceded by a reading phase. Well inside the ~40 min / ~40 call target.

---

## Next concrete action

**One successor, and it is not more computation.** Put exactly one question to the rule's owner, in this form: *does the site-curation principle "Pool membership is decided per pool, not once per source" govern the registry's `who_ever_metastasises` and `who_recurs_locally` pools, or only the site pool?* That single answer resolves everything above — **yes → R3** (metastasis 107/300 = 35.7%, recurrence unchanged, no registry byte changes, no deposit re-stamp), **no → R0** (nothing moves) — and it needs no data at all. **R1 should be struck from the option set outright: it is a measured no-op, and offering it as a choice would waste the owner's reading.** R2 is the only option that both edits a deposited file and rests on the unchecked overlap premise, so it should not be chosen until item 1 of the missing-evidence list is unblocked — and that item is currently blocked.

⚠ Independently of the clause, one defect is worth its own successor: **the two pooled figures the ASO working record quotes (36.3%, 27.0%) are pinned by no test** (D12). That is a gap the owner should close whichever way the clause goes, and it belongs to whoever owns `research/modalities/tests/`, not to lane 16.
