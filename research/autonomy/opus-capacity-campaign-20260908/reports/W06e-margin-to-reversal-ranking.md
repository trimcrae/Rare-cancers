> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report below.

---

## Worker

- **Worker ID:** W06e — Lane 6 refill, successor to W06d, in OPUS-CAPACITY-CAMPAIGN-20260908.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt. I did not observe the served model, and **no environment variable in this container names a model** — the `env` grep below contains no model identifier, so the self-report has no environmental corroboration. The coordinator must extract the actual runtime model from the child transcript.
- `date -u` at **start**: `Tue Sep  8 02:49:35 UTC 2026`. At **end**: `Tue Sep  8 02:53:07 UTC 2026`.
- **HEAD actually read at start: `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`.** At end: `4d950cf036294627b7ae67dfb306cc1875d702ac` — HEAD moved under me mid-run (the coordinator committing other workers' reports). I verified this does not affect anything I read: `git diff --stat 3f5fc95 4d950cf --` over all five files I used returned **empty output, exit 0** — the decomposition artifact, its inputs, the generator, the mortality-mechanisms paper and the clinical registry are byte-identical across the two commits. Note also that both differ from the frozen read commit named in COMMON-BRIEF.md §1 (`92abbcb…`); I read the checkout as it stands and say so.
- `git status --porcelain` at **start**: empty. At **end**: empty. **I wrote nothing into the Git tree.** All execution under `/tmp/claude-0/w06e/`.
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`:

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

## Question

**Which quantitative conclusion committed in this lane's repository artifacts and manuscripts sits closest to its own tipping point, and how far is it?**

W06b, W06c and W06d each held one quantity fixed and moved another, and each answered a question about its *own* swept parameter. None of them asked the cross-cutting question: across the whole set of committed assertions this lane owns, which one reverses first, measured in the units of the input that would have to move. That is open because no artifact in the lane carries a margin field for any conclusion except the two W06d proposed and did not apply (`impossible_fraction`, `quotable_by_own_rule`), and those cover one field of one horizon.

I set the stop condition **up front**: return the moment every committed quantitative conclusion in the lane is enumerated with `file:line`, has a margin-to-reversal in its input's own units, is ranked, and the most fragile one is confirmed by a real command with a real exit code rather than by algebra.

## Prior-work check

```
$ rg -n "emc-mortality-decomposition|emc_mortality_decomposition|mortality decomposition" \
     --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**' -l
```
→ 21 files. The consumers that matter: `research/manuscripts/emc-mortality-mechanisms-paper.md` (the paper), `research/manuscripts/emc-mortality-mechanisms.md` (the memo), `systems/views/L2-rt-competing-mortality.md`, `systems/graph/routes.json`, `research/autonomy/research-ledger.json`.

```
$ rg -n "58\.6|1\.77|30\.8|39\.4|57\.1" research/manuscripts/*.md systems/views/ systems/graph/ \
     research/autonomy/research-ledger.json
$ grep -n -i "cross-series|five-year|5-year|58\.6" research/manuscripts/emc-mortality-mechanisms-paper.md
$ git ls-files | rg -i "mortality.decomposition"
```

What these showed, and it is load-bearing for the ranking: **the paper quotes no cross-series figure at all.** Its only "five-year" mentions are line 262 (the japan2003 selection signal) and line 398 (the nMx erratum). The memo quotes the 10-year band at line 85. So `cross_series["5_year"]` — the block W06c and W06d both centred on — is **internal to the artifact**, not load-bearing for the near-published paper.

`CLOSED-WORK.md` and `CORPUS-CONTEXT.md` read in full. Confirmed not replayed: **PUB-EMC-CLASSIFICATION / the user-rejected registry ICD-O classification paper — I ran no EMC calibration analysis and introduce no contamination parameter of my own**; Brenca, Hofvander, paired Davis, promoter transfer, GSE4303/GSE28866 (all untouched); every unrecovered source (no retrieval, no network); lane 11 source-index (untouched). I did not re-derive W06c's tipping point — **π = 0.130 is reused as a stated input below and labelled as such**; I did not re-run W06b's pool sweep; I did not apply or re-derive W06d's patch.

## Method / inputs

Read-only on the tree. Sandbox `/tmp/claude-0/w06e/` mirrors the repository paths so the generator's `ROOT = Path(__file__).resolve().parents[2]` resolves inside the sandbox and never to `/home/user/Rare-cancers`.

Inputs, all copied verbatim from HEAD `3f5fc95` (and verified identical at `4d950cf`):
- `/home/user/Rare-cancers/research/manuscripts/emc-mortality-decomposition.json` (238 lines, the committed artifact)
- `/home/user/Rare-cancers/research/manuscripts/emc-mortality-decomposition-inputs.json` (195 lines)
- `/home/user/Rare-cancers/research/manuscripts/emc_mortality_decomposition.py` (512 lines)
- `/home/user/Rare-cancers/research/manuscripts/emc-mortality-mechanisms-paper.md` (408 lines, PUB-MORTALITY-MECHANISM)
- `/home/user/Rare-cancers/research/data/emc-clinical-registry.json` (the one home of every clinical figure)
- `/home/user/Rare-cancers/systems/POLICY-evidence.md` (read in full; §2.1's ban on deriving a count from a percentage governs every margin below — no denominator here is back-derived)

Reused as stated inputs, not recomputed: W06c's model-C tipping point **π = 0.130** and its closed form *"a coherent pairing flips to impossible exactly when π exceeds its own competing share"*; W06d's `IMPOSSIBLE_FRACTION_QUOTABLE_MAX = 0.5` reading of the file's own rule.

Tools: `python3` 3.11.15, stdlib only, Linux 6.18.44-fc-v24. No network. The Wilson function used for the background-check margins is **the generator's own `wilson()`**, imported from the sandbox copy by `importlib`, not a reimplementation.

## Result

### 1. The enumeration — every quantitative conclusion the lane's committed files assert

`L` = load-bearing for the near-published paper (PUB-MORTALITY-MECHANISM, state `preprint`); `I` = internal to an artifact, memo, route or ledger.

| # | `file:line` | The assertion, exactly | class | evidence |
|---|---|---|---|---|
| A1 | `research/manuscripts/emc-mortality-mechanisms-paper.md:70-72` | "Of 52 deaths … 15 (28.8 per cent) carried any stated mechanism. Among those 15, death from a competing cause or a second malignancy was the largest category (6 deaths, 40 per cent), **exceeding respiratory failure (3 deaths)**" | **L** | PRIMARY |
| A2 | `…paper.md:74-76`, `…paper.md:239-240`, `research/manuscripts/emc-mortality-decomposition.json:18` and `:35` | competing share **30.8 %** localised (4 of 13) and **10.0 %** metastatic (1 of 10); ordering localised > metastatic | **L** | PRIMARY |
| A3 | `…paper.md:76-78`, `…paper.md:239-240,244-246`, `decomposition.json:19` and `:36` | antitumour ceiling **6.7 points** localised vs **31.0 points** metastatic; "the value … is concentrated in the stratum that is the minority of patients" | **L** | PRIMARY |
| A4 | `…paper.md:78-80`, `…paper.md:255-258` | relative survival median competing share **23.0 %** (range 12.1–45.4) vs **21.7 %** from the cause split; "the two share no input" | **L** | PRIMARY |
| A5 | `…paper.md:80-81`, `…paper.md:267-270`, `decomposition.json:199-209` | localised: 3.0 % observed vs 3.1 % expected, **ratio 0.97 (95 % CI 0.38–2.41)**, `background_inside_observed_ci: true` | **L** | PRIMARY |
| A6 | `…paper.md:269-270`, `decomposition.json:218-228` | metastatic: 3.4 % vs 3.3 %, **ratio 1.04 (95 % CI 0.18–5.18)**, `background_inside_observed_ci: true` | **L** | PRIMARY |
| A7 | `…paper.md:248-251` | distant metastasis associated with tumour death, **OR 26.26 (95 % CI 2.99–231.04)**; local recurrence not associated | **L** | SECONDARY (quoted from masunaga2025, not computed here) |
| A8 | `…paper.md:81-82`, `…paper.md:382` | "No publication reporting the growth rate of pulmonary metastases in this disease was found" | **L** | PRIMARY negative |
| A9 | `decomposition.json:86-94` | 5-year cross-series: **12 pairings, 6 coherent, 6 impossible**; competing share range [13.0, 70.0], **median 58.6** | **I** | PRIMARY |
| A10 | `decomposition.json:133` (and `:181`) | the file's own rule: **"A horizon where most pairings are impossible should not be quoted at all"** | **I** (a gate, not a number) | PRIMARY |
| A11 | `decomposition.json:154-162` | 10-year cross-series: **6 pairings, 4 coherent, 2 impossible**; share range [50.0, 57.1], median 57.1 | **I** (memo `emc-mortality-mechanisms.md:85` quotes the band) | PRIMARY |
| A12 | `decomposition.json:48-49` | within-series Meis-Kindblom 10-year competing share **39.4 %**, ceiling 18.2 points | **I**, and explicitly **superseded-retained** at `emc-mortality-mechanisms.md:390,395` and `…paper.md:391` | PRIMARY |
| A13 | `decomposition.json:188-191` | whole-cohort background check: expected 11.3 % vs observed 20.0 % at 10 y, **ratio 1.77**, with the stated gate "A ratio far above 1 … the decomposition is an artifact and must not be quoted" | **I** (routes.json:8963, research-ledger.json:316 quote it; the paper does **not**) | PRIMARY |
| A14 | `decomposition.json:6` | directional-bias statement: censoring other-cause deaths makes the competing share an **UNDER-estimate**, so the bias runs against the conclusion | **L** (sign claim, no number) | PRIMARY |

### 2. Margin to reversal, in each input's own units

Every margin below is the smallest perturbation of a **committed input** that flips the assertion's direction or crosses its **stated** threshold. Where the input carries no stated uncertainty, I say so; **an unstated uncertainty is UNKNOWN, never zero.** I confirmed by direct read that the clinical registry states **no confidence interval on any survival percentage** — `sorted(set(re.findall(r'"(ci[0-9]*|confidence[A-Za-z]*)"', json.dumps(registry))))` returns `[]`.

| # | Input that must move | Margin, in that input's units | As a fraction of the input's **stated** uncertainty | class |
|---|---|---|---|---|
| A9 + A10 | `pairings_impossible` at the 5-year horizon | **ZERO in pairing units.** 6 of 12 is *exactly* the boundary of "most"; one further flip (7/12) breaches the file's own do-not-quote gate. Equivalently, in the units of the survival figures that produce it: **1.30 percentage points** on `masunaga2025_localized` five-year DSS (91.3 % → 90.0 % is the last coherent value), or **1.30 points** on `meisKindblom1999` five-year OS (90.0 % → 91.3 %) | **UNKNOWN** — neither 91.3 % nor 90 % carries a stated interval. Against the only *implied* uncertainty, the rounding of "90 %" to whole per cent (half-width 0.5 pp), the margin is **2.6 ×** that half-width — rounding alone cannot flip it | PRIMARY, verified by execution (§3) |
| A6 | other-cause deaths in the metastatic stratum, committed **1 of 29** | **+2 events.** At 3/29 the Wilson interval becomes [3.58, 26.39] % and 3.3 % expected falls outside → `background_inside_observed_ci` flips to false. It **never** flips downward: 0/29 gives [0.00, 11.70] %, still containing 3.3 % | the stated uncertainty *is* the Wilson interval, which the margin is defined against; 2 events out of a 29-patient stratum = **6.9 pp** of that stratum | PRIMARY |
| A5 | other-cause deaths in the localised stratum, committed **4 of 134** | **+5 events** (9/134 → CI [3.57, 12.27] %, excludes 3.1 %) or **−4 events** (0/134 → CI [0.00, 2.79] %, excludes 3.1 %). So the two-sided margin is 4 events down, 5 up | as above; 4 events = **3.0 pp** of a 134-patient stratum | PRIMARY |
| A1 | classification of the 15 mechanism-stated deaths | **2 reclassifications.** Moving 1 death from the 6-death composite to respiratory gives 5 vs 4 — still "exceeding"; moving 2 gives 4 vs 5 — reversed. 2/15 = **13.3 %** of the classified deaths. ⚠ **Separately: the margin is ZERO against a grouping change** — the composite is `competing non-cancer (3) + second malignancy (3)` against `respiratory failure (3)` (`paper.md:194-196`); dissolve the grouping and there is a three-way tie at 3, with no category exceeding any other. That is a definitional choice, not an input perturbation, and I score it separately for that reason | **UNKNOWN** — Table 1 is a count table with no stated classification uncertainty. There is 1 death in an explicit `ambiguous` category, which is the nearest thing to a stated uncertainty and is **1** of the 2 reclassifications the reversal needs | PRIMARY |
| A2 | cause attributions in masunaga2025 | **3 deaths.** Localised must fall from 4/13 (30.8 %) to at most metastatic's 10.0 %, i.e. to 1 of 10 after 3 reattributions | **UNKNOWN** — no interval is stated on either share in the paper or the artifact | PRIMARY |
| A7 | the odds ratio itself | **1.0953 log-units** — the distance from the CI's lower bound ln(2.99) = 1.0953 down to the null ln(1) = 0 | **0.50** — exactly half the interval's own log half-width, (ln 231.04 − ln 2.99)/2 = 2.174. **This is the only conclusion in the lane whose input carries a real stated uncertainty**, and its margin is half of it | SECONDARY (source-quoted) |
| A11 | `pairings_impossible` at 10 years | **1 pairing of slack** — 2/6 now; 3/6 is still quotable under "most" = strictly more than half; 4/6 breaches. Via W06c's closed form, the smallest 10-year coherent share is 50.0 %, so **50.0 pp** of share | **UNKNOWN** — no stated interval on the underlying figures | PRIMARY, reusing W06c |
| A4 | the convergence 21.7 % vs 23.0 % | **no reversal exists** in the perturbation W06b swept: no tipping point at any π in [0, 1). Only 4 of 8 pooled shares can move; the upper median is floored at 12.1 %, inside the cause-split range [10.0, 30.8] | n/a — the assertion has no reachable boundary under that input | reused from W06b, PRIMARY there |
| A3 | disease deaths in the localised stratum | **+32 deaths.** Localised disease mortality would have to rise from 9/134 (6.7 %) past 31.0 %, i.e. to 42 of 134 | **UNKNOWN**, and the perturbation exceeds the cohort's entire observed death count (13) | PRIMARY |
| A13 | the whole-cohort ratio 1.77 against "far above 1" | **UNCOMPUTABLE — the threshold is not stated.** "Far above 1" is prose with no number. The margin is therefore **UNKNOWN, not zero and not infinite**. What is checkable: 1.77 is already the largest of the three ratios on record and the paper answers this gate by quoting the two per-stratum checks (0.97, 1.04) instead, never the 1.77 | **UNKNOWN** | PRIMARY (the value); UNKNOWN (the margin) |
| A8, A14, A12 | — | Not margin-bearing. A8 is a search-negative ("no publication found"), reversible only by a retrieval this campaign forbids; A14 is a sign claim following from the estimator's construction, not from a movable input; A12 is already marked superseded-retained and asserts nothing current | n/a | — |

### 3. The ranking, and the direct-execution verification of the top item

**Ranked by fragility (smallest reversal first):**

1. **A9/A10 — the 5-year cross-series block against the file's own quotability rule.** Margin **zero** in pairing units, **1.30 pp** in survival-percentage units. **Internal, not quoted in the paper.**
2. **A1 — "exceeding respiratory failure".** 2 of 15 reclassifications; **zero** against the grouping choice. **Load-bearing (abstract and §3.1).**
3. **A6 — the metastatic background-consistency check.** +2 events on a committed 1. **Load-bearing (abstract and §3.6).**
4. **A11 — the 10-year cross-series block.** 1 pairing of slack. Internal; the memo quotes the band.
5. **A5 — the localised background-consistency check.** +5 / −4 events on a committed 4. Load-bearing.
6. **A7 — the odds ratio.** Half its own stated interval. Load-bearing, and the only one measurable against a real stated uncertainty.
7. **A2 — the 30.8 % > 10.0 % ordering.** 3 reattributions. Load-bearing.
8. **A4 — the 21.7 % / 23.0 % convergence.** No reversal reachable under the swept parameter. Load-bearing and **robust**.
9. **A3 — the 6.7 vs 31.0 ceiling ordering.** +32 deaths, more than the cohort's observed deaths. Load-bearing and **robust**.
10. **A13 — the 1.77 whole-cohort ratio.** Margin **UNKNOWN**; the gate it must clear has no number.

**Verification of the most fragile by direct execution, not algebra.** I perturbed only the numeric field `series[masunaga2025_localized].disease_specific_survival["5"]` in a sandbox copy of the committed inputs and re-ran the **unmodified committed generator**, five values, each a real run:

| `fiveYearDSS` | exit | `cross 5_year` line, verbatim from stdout |
|---|---|---|
| **0.913** (committed) | 0 | `competing share [13.0, 70.0]% (median 58.6%) … 6/12 pairings coherent (6 impossible, 0 undefined)` |
| 0.9005 | 0 | `competing share [0.5, 65.7]% (median 52.6%) … 6/12 pairings coherent (6 impossible, 0 undefined)` |
| **0.9000** | 0 | `competing share [0.0, 65.5]% (median 52.4%) … 6/12 pairings coherent (6 impossible, 0 undefined)` ← last coherent |
| **0.8995** | 0 | `competing share [16.6, 65.3]% (median 52.1%) … 5/12 pairings coherent (7 impossible, 0 undefined)` ← **flipped** |
| 0.8990 | 0 | `competing share [16.6, 65.2]% (median 51.9%) … 5/12 pairings coherent (7 impossible, 0 undefined)` |

The flip lands between 0.9000 and 0.8995 — i.e. at exactly the committed competing share of that pairing, 13.0 %, which is what W06c's closed form predicts and which I am here confirming by execution rather than re-deriving. The symmetric route flips too: raising `meisKindblom1999` five-year OS from 0.90 to **0.914** gives `5/12 pairings coherent (7 impossible)`, exit 0.

Two consequences visible in that table and worth recording separately:
- At 7/12 impossible the horizon **breaches its own do-not-quote rule** — W06d's `quotable_by_own_rule` would read `false`.
- The **published median moves 58.6 → 51.9, a 6.7-point swing, for a 1.4-point input change** — leverage of roughly 4.8×. The median is the least stable number in the artifact even where the coherence verdict holds.

### 4. The honest headline: the load-bearing conclusions are robust; the fragile one is not published

**Report a robust result as readily as a fragile one — and this lane's result is mostly robust.** Every conclusion the paper actually asserts survives a perturbation at least as large as its own event count or larger, with two exceptions of moderate size (A1 at 2 reclassifications, A6 at +2 events). The one conclusion sitting at literal zero margin, A9/A10, **is not quoted in the paper** — the memo and the ledger record that the 5-year pairing "breaks down and is not quoted", and my grep confirms the paper contains no cross-series figure at all. The lane's most fragile quantity was already fenced off from publication before this analysis, by the authors, deliberately. That is the finding.

**Perturbations I judged implausible, and why — I did not use any of them to manufacture fragility:**
- **Raising `japan2003`'s 100 % five-year OS.** It is at the ceiling and cannot rise; lowering it makes pairings *more* coherent. This is a safe-direction input and offers no reversal route, so I did not score it.
- **Moving SEER's 76 % five-year OS by the >15 pp needed to change a coherence verdict.** n = 270, the least selected series in the registry; a shift of that size is a different study, not a perturbation.
- **Adding 32 disease deaths to the localised stratum (A3).** That exceeds the cohort's entire observed death count of 13. It is arithmetic, not a scenario.
- **Introducing any misclassification parameter of my own.** PUB-EMC-CLASSIFICATION is user-rejected and closed and no new EMC calibration may be admitted on unchanged inputs. W06c's π is reused as a stated input and nothing more.
- **Substituting a different life table for WHO GHO USA 2021.** That is source substitution, which CLOSED-WORK forbids as a reasoning route, and it would change the check's identity rather than perturb its input.
- **Treating the rounding of published percentages as the operative uncertainty.** I report it (0.5 pp on "90 %") because it is the only implied uncertainty available, but rounding is 2.6× too small to flip A9, so it is a floor on the margin, not a reversal route.

## Validation evidence

Environment for every command: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `python3` 3.11.15 stdlib only, working directory `/tmp/claude-0/w06e/`, **no network used**, repository read at HEAD `3f5fc95` (files verified identical at `4d950cf`).

**RUN — 1. Baseline fidelity. The sandbox reproduces the committed artifact byte-for-byte.**
```
$ cd /tmp/claude-0/w06e/base && python3 research/manuscripts/emc_mortality_decomposition.py
wrote research/manuscripts/emc-mortality-decomposition.json
  DIRECT  Japanese national registry, localised surgical: 4/13 deaths were not EMC deaths = 30.8% (ceiling 6.7 pts)
  DIRECT  Japanese national registry, metastatic at diagnosis: 1/10 deaths were not EMC deaths = 10.0% (ceiling 31.0 pts)
  within  Meis-Kindblom 1999 pathology series: at 10y, 39.4% of deaths were not EMC deaths (antitumour ceiling 18.2 pts)
  cross   5_year: competing share [13.0, 70.0]% (median 58.6%), ceiling [8.7, 24.2] pts, 6/12 pairings coherent (6 impossible, 0 undefined)
  cross   10_year: competing share [50.0, 57.1]% (median 57.1%), ceiling [15.0, 15.0] pts, 4/6 pairings coherent (2 impossible, 0 undefined)
  background check: RUN
  BG localised: observed 3.0% vs background 3.1% -> ratio 0.97 (95% CI 0.38-2.41)
  BG metastatic: observed 3.4% vs background 3.3% -> ratio 1.04 (95% CI 0.18-5.18)
BASE_EXIT=0
$ cmp /tmp/claude-0/w06e/committed.json /tmp/claude-0/w06e/base/research/manuscripts/emc-mortality-decomposition.json
CMP_EXIT=0
```

**RUN — 2. The five-value flip sweep and the symmetric check.** Full table in §3 above; every run `EXIT=0`; the generator's `verify_provenance` gate passed on every run (it checks `registry_verbatim` strings, which I did not touch — only the numeric field).

**RUN — 3. Background-check margins, using the generator's own `wilson()` via `importlib`.** Verbatim excerpt:
```
-- localised: n=134, expected background 3.1%, committed events=4
   events= 0  pct= 0.00  CI[ 0.00, 2.79]  background_inside=False
   events= 4  pct= 2.99  CI[ 1.17, 7.42]  background_inside=True  <-- COMMITTED
   events= 8  pct= 5.97  CI[ 3.06,11.34]  background_inside=True
   events= 9  pct= 6.72  CI[ 3.57,12.27]  background_inside=False
-- metastatic: n=29, expected background 3.3%, committed events=1
   events= 0  pct= 0.00  CI[ 0.00,11.70]  background_inside=True
   events= 1  pct= 3.45  CI[ 0.61,17.18]  background_inside=True  <-- COMMITTED
   events= 2  pct= 6.90  CI[ 1.91,21.96]  background_inside=True
   events= 3  pct=10.34  CI[ 3.58,26.39]  background_inside=False
```

**RUN — 4. Registry uncertainty audit.** `sorted(set(re.findall(r'"(ci[0-9]*|confidence[A-Za-z]*)"', json.dumps(registry))))` → `[]`; the four cohorts I depend on carry `fiveYearDSS` / `n` / `studyPeriod` and no interval.

**RUN — 5. HEAD-move safety.** `git diff --stat 3f5fc95 4d950cf -- <the five files>` → empty output, exit 0.

**PROPOSED (NOT RUN):** nothing. I proposed no patch, applied none, and ran `scripts/preflight.sh` not at all (my dispatch does not authorise it).

## Limitations

- **This is a sensitivity analysis of committed numbers, not a measurement of anything about patients.** No margin here says any input *is* wrong, that any death was misattributed, or that any cohort contains a misclassified tumour. A margin is a distance, and a distance is not a direction of travel.
- **No clinical claim, and none is derivable from this.** Nothing here bears on diagnosis, classification, treatment selection, prognosis or clinical practice, and I make no recommendation about any of them. The §2.5 limitations of `systems/POLICY-evidence.md` apply in full to every quoted figure.
- **The dominant uncertainty in this lane is unstated, and that is the real limitation.** Nine of the fourteen assertions rest on survival percentages carrying **no confidence interval anywhere in the registry**. Every "fraction of stated uncertainty" cell for those reads UNKNOWN. The apparent tightness of the 1.30-pp margin on A9 is therefore not comparable to the apparent looseness of A7's margin — one is measured against nothing and one against a real interval.
- **A1's margin has two units and they disagree.** Two reclassifications against an input perturbation; zero against a grouping choice. I report both rather than picking the smaller and calling it the answer, because the grouping is an authorial decision that a reader can see in Table 1 and re-take for themselves.
- **A13's margin is genuinely uncomputable**, not merely large. A gate written as "far above 1" cannot be crossed or cleared by arithmetic. I did not assign it a number.
- **W06c's π and W06b's pool sweep are reused as inputs and inherit their own limitations**, including that π is a swept hypothetical with no measured counterpart in this repository.
- **I checked only the lane's own committed artifacts.** Other consumers of these numbers may exist outside the 21 files my `rg` returned; a file my search did not reach is UNKNOWN, not absent.
- Single-worker analysis, no independent replication of my own margin arithmetic beyond the executed runs.

## Stop condition

**Set up front:** return the moment (i) every quantitative conclusion in the lane's committed artifacts and manuscripts is enumerated with `file:line`, (ii) each has a margin-to-reversal in its input's own units with stated uncertainty named or marked UNKNOWN, (iii) the set is ranked, and (iv) the most fragile is confirmed by a real command with a real exit code.

**MET.** 14 assertions enumerated (A1–A14), 10 with computed margins, 3 correctly identified as not margin-bearing, 1 (A13) with an honestly uncomputable margin; ranked; the top item verified by five executed generator runs bracketing the flip at 0.9000 / 0.8995, all exit 0, plus the symmetric confirmation at 0.914. Returning now.

## Tool-call and wall-clock count actually used

**16 tool calls** (all Bash) against a ~40 target. **Wall clock 02:49:35Z → 02:53:07Z = 3 min 32 s** against a ~40 min target. Nothing was padded and nothing was left running.

## Next concrete action

**Extend W06d's routed-but-unapplied `quotability()` readout to emit a margin in the units the input actually moves in, not only in pairings.** W06d's patch emits `impossible_fraction` and `quotable_by_own_rule`; this report shows that the pairing-unit margin (zero) and the survival-percentage margin (1.30 pp) are different numbers with different reader consequences, and only the second tells anyone how close the artifact is to its own gate. The concrete task: add one field per horizon, `smallest_coherent_share_pct` — which by W06c's closed form **is** the margin, needs no sweep, and for the committed file reads 13.0 at 5 years and 50.0 at 10 — so a reader sees "this horizon is one 13-point move from being unquotable" without running anything. It changes no published number (the paper quotes no cross-series figure at all), it is a readout of values already in the artifact, and it belongs to the generator's owner to apply. Lane 6 owns it.

I did **not** nominate the obvious alternative — instrumenting A1's grouping sensitivity in the paper — because that would edit a near-published manuscript's Results on an internal analysis's say-so, and the paper's own Table 1 already prints the three underlying counts where a reader can see the tie.
