<!-- collected 2026-09-08T04:57:32Z by campaign coordinator; agent id aceba6c9e07706bd8; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aceba6c9e07706bd8.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted; report follows.

## Worker

**W68**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: evidence-contract enforcement — W53's named successor. Read-only locate-and-compare.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in the environment corroborates it; no variable names a model. The coordinator must extract the served model from the transcript.

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

**Start** — `date -u` → `Tue Sep  8 04:51:31 UTC 2026`; `git rev-parse HEAD` → `56f355f65b7b3e47aeb434ac02edf4cf049f40f3`; `git status --porcelain` → **empty**.
**End** — `date -u` → `Tue Sep  8 04:54:37 UTC 2026`; `git rev-parse HEAD` → `fcb36d3c651223d90b98c0cb64169bb106e6e060` (HEAD advanced under me — coordinator collecting reports); `git status --porcelain` → **empty**.

**Write isolation honoured.** Zero repository writes, zero git write operations, no network, no MCP call, no publication. **I did not run `research/meta/meta-analysis.mjs` at all** — not in the live tree and not in a copy; every number I needed was already in the committed `research/meta/results.json`, and my independent Wilson arithmetic ran as a heredoc `python3` with `cwd=/tmp/claude-0/w68`, reading the repository by absolute path and writing nothing. Scratch (`/tmp/claude-0/w68/`, three file lists) deleted: `ls /tmp/claude-0/w68` → `No such file or directory`. I authored no repair, patch, gate or test; touched no manuscript, module or policy; ran no `preflight.sh`; did not invoke `atr_hrd_sarcoma_series.py`. W25 not read, not referenced.

## Question

Which of the two pooled headlines does the manuscript actually print — the DerSimonian–Laird random-effects figure `research/meta/meta-analysis.mjs` writes, or POLICY-evidence §2.2's crude denominator-weighted pool with Wilson intervals — and does `research/manuscripts/pinned-figures.json` pin a value from one method while citing the other's section?

Open because W53 measured the two methods and found the recurrence interval **3.3× wider** under DL, but its grep for the literal strings `27.8`, `37.9`, `14.2%`, `90.4`, `69.1` in `pinned-figures.json` and `research/manuscripts/*.md` returned no hits — recorded as UNKNOWN, not absence.

## Prior-work check

W53's hypothesis for the null grep was correct on both counts: **different formatting** (the manuscript rounds to whole percents — `28%`, not `27.8`) **and a subdirectory not walked** (`research/manuscripts/*.md` does not glob `research/manuscripts/endpoint/`). Commands run:

```
$ git ls-files | grep -v '^research/autonomy/opus-capacity-campaign-20260908/'   # 7600 files
$ xargs -a <that list> grep -n -E '(27\.8|26\.99|27\.0%|37\.9|36\.29|36\.3%|14\.19|14\.2%|13\.7%|88/326|94/259|36/262|47\.3|49\.6|22\.63|32\.06|32\.1%|42\.3%|18\.4%)'
$ xargs -a <text files> grep -n -i -E 'wilson|dersimonian|random.effects'
$ xargs -a <text files> grep -n -E '88/326|94/259|36/262|/326|/259|/262'
$ grep -rn -E '(2[678]|3[678]|1[34])(\.[0-9])?%' … | grep -i 'pooled' | grep -i 'recurr|metasta|death'
$ grep -rn "meta/results.json" --include='*.py' --include='*.mjs' --include='*.md' --include='*.json' .
$ grep -rn 'endpoint/meta-analysis' --include='*.py' --include='*.mjs' --include='*.yml' --include='*.json' .
$ python3 -c "… json.dumps(pinned-figures.json).count(<term>) …"
```

Read in full first, as dispatched: `COMMON-BRIEF.md` (478 l), `CORPUS-CONTEXT.md` (82 l), `CLOSED-WORK.md` (70 l), `systems/POLICY-evidence.md` §2 (§2.1–§2.6 plus the two-methods callout), and W53's report. **Taken as given, not replayed:** W53's arithmetic verification (module ≡ independent Python to 1.42e-14) and W47's 183-entry `pinned-figures.json` consumer map (160 ENFORCED / 23 READ-BUT-NOT-COMPARED / 0 UNREAD). The 0-of-89 backlog untouched.

## Method and inputs

- **Policy text:** `systems/POLICY-evidence.md:117-186` (callout + §2.1–§2.5).
- **DL numbers:** read from the committed `research/meta/results.json` — not regenerated.
- **Crude/Wilson numbers:** recomputed by me in Python 3 stdlib (`math` only) from the study rows in `results.json`, using the Wilson score interval with z = 1.959963984540054.
- **Corpus walk:** `git ls-files` minus the campaign directory (7,600 files), searched with `xargs … grep`; binary/`.eps`/`.csv` excluded for the prose passes only.
- Tools: `git`, `grep`, system `python3`. No `node`. No network, no MCP, no retrieval.

## Result

### A. The two computations (PRIMARY — recomputed by me this run)

| Metric | Σe/Σn | **DL (module, committed `results.json`)** | **§2.2-as-written: crude + Wilson (my computation)** |
|---|---|---|---|
| recurrence | 88/326 | 27.84% (14.21–47.34), I²=90.4 | **26.99% (22.46–32.06)** |
| metastasis | 94/259 | 37.90% (27.48–49.58), I²=69.1 | **36.29% (30.68–42.31)** |
| diseaseDeath | 36/262 | 14.19% (8.55–22.63), I²=61.6 | **13.74% (10.09–18.44)** |

Reproduces W53's table exactly. Every figure below is classified by matching against these two columns.

### B. Every location in the tracked corpus that states a pooled EMC recurrence / metastasis / disease-specific-death figure

| Location | Figure as printed | Which method | Pinned? | Cited section |
|---|---|---|---|---|
| `research/manuscripts/endpoint/meta-analysis.md:37-39` (Abstract, Results) | recurrence **28% (95% CI 14–47%, I²=90%)**; metastasis **38% (28–50%, I²=69%)**; DSM **14% (9–23%)** | **DL** — named in the same sentence ("random-effects pooled") | **NO** | §2 Methods (`:33-34`) names DerSimonian–Laird; no POLICY-evidence § number cited anywhere in the file |
| `research/manuscripts/endpoint/meta-analysis.md:134-136` (§3.2 table) | RE column: **28% / 14–47% / I²=90 / τ²=0.67 / k=4**; **38% / 28–50% / 69 / 0.12 / 3**; **14% / 9–23% / 62 / 0.10 / 2**. Separate column headed `(crude, Wilson)`: **27% (22–32%)**, **36% (30–42%)**, **14% (n=266)** | **BOTH, side by side and correctly labelled.** RE column = DL; the parenthetical column = crude+Wilson | **NO** | Column header names Wilson; no § number |
| `research/manuscripts/endpoint/meta-analysis.md:147` (forest table, pooled row) | **88 / 326 · 28% (14–47%) · I²=90%** | **DL** (denominator is the crude Σ; estimate and CI are DL) | **NO** | — |
| `research/manuscripts/endpoint/meta-analysis.md:157-165` (§3.3) | I²=90%; interval widened to **14–47%**; registry-only **12% (7–19%)** vs older/undated **39% (22–59%)**; LOO **22–36%**; era **19% (7–43%)** vs **39% (22–59%)**; registry-only vs all-series **12% vs 28%** | **DL** (all match `results.json` sensitivity/LOO fields to rounding) | **NO** | — |
| `research/manuscripts/endpoint/meta-analysis.md:175-186` (§4 Discussion) | metastasis **38% (28–50%)**; recurrence **28% (14–47%)**; mortality **14%**; registry 12% (7–19%), all-series 28%, older 39% (22–59%); LOO 22–36% | **DL** | **NO** | — |
| `research/manuscripts/endpoint/meta-analysis.md:205` (§5 Limitations) | recurrence **I²=90%** | **DL** | **NO** | — |
| `research/modalities/emc-locoregional-eligibility.json` → `who_recurs_locally` | **88/326 = 27.0% (22.5–32.1%)**, `interval: "Wilson score, 95%"`; per-cohort range 11.9–48.2 | **crude + Wilson** | **NO** | `_method.contract`: *"systems/POLICY-evidence.md §2 (binding)"*; `estimator` field cites **§2.2, §2.4**; `not_used` explicitly names the DL pooler and the callout's "real error" warning |
| `research/modalities/emc-locoregional-eligibility.json` → `who_ever_metastasises` | **94/259 = 36.3% (30.7–42.3%)**, Wilson; per-cohort range 29.1–46.1; metastatic-at-dx cohort excluded with the reason *"⛔ inclusion criterion IS the outcome (POLICY-evidence §2.1.3)"* | **crude + Wilson** | **NO** | §2.2, §2.4 (and §2.1.3 for the exclusion) |
| `research/manuscripts/aso/fusion-junction-aso-working-record.md:1318` | **36.3% (94/259, Wilson 95% CI 30.7–42.3%)**, attributed to `emc-locoregional-eligibility.json` and *"not re-derived here"* | **crude + Wilson** | **NO** | names the owning artifact, not a § number |
| `research/PROTOCOL.md:74-77`, `research/README.md:95-96`, `CONTRIBUTING.md:94`, `systems/POLICY-evidence.md:121-130` | method descriptions only — no pooled value | n/a | **NO** | all four state the two-method split correctly |

**No disease-specific-death figure is printed anywhere outside `meta-analysis.md`.** `emc-locoregional-eligibility.json` has no `who_dies_of_disease` block.

**Adjacent but a different estimand, so excluded from the table above** (recorded so a successor does not mistake them for the headline): `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md` / `emc-fusion-partner-pooling.json` pool *by fusion partner* over 73 patients (e.g. disease-specific death 7/15 = 46.7%, 24.8–69.9), and `research/modalities/emc_rt_bed_reappraisal.py` pools local control by RT modality. Both use crude proportions + Wilson, both explicitly record refusing DL for their k and event counts (`emc_fusion_partner_pooling.py:30,2030-2034`; `emc_rt_bed_reappraisal.py:386-387`). Neither is one of the three headline pools.

### C. Direct answers

1. **The manuscript prints the DL figure as its headline, and prints the crude/Wilson figure beside it in one table cell, correctly labelled.** `research/manuscripts/endpoint/meta-analysis.md` is the only document that prints any of the three headline pooled values. Its §2 Methods (`:95-99`) states the arrangement in advance: *"For the manuscript we pool logit-transformed proportions by random effects (DerSimonian–Laird) … A crude denominator-weighted proportion with a Wilson 95% CI is reported alongside as the conservative floor."* The abstract, §3.3, §4 and §5 quote the DL numbers only. **No location in the tracked corpus quotes one method's number while naming the other method** — the §2 callout's "real error" is not committed anywhere I could find.

2. **`pinned-figures.json` pins none of these values, so the cross-method mis-citation it was asked about cannot exist there.** Measured, not inferred: its `targets[]` is a flat list of **29 paths** and `research/manuscripts/endpoint/meta-analysis.md` **is not among them**; over the whole file, `json.dumps(...).count()` is **0** for `recurrence`, `metasta`, `diseaseDeath`, `meta-analysis`, `results.json`, `emc-clinical-registry`, `POLICY-evidence` and `DerSimonian`. Its 5 `Wilson` hits are all ASO/vaccine binomial intervals (`aso_ewsr1_partner_share_wilson_upper_87_8`, `vaccine_coverage_wilson_intervals`, and one `context` regex), unrelated to EMC outcome pooling. This is the expected consequence of W51's measured result — `lint_consistency.py` reads only literal paths from `pinned-figures.json`, and 171 of 187 tracked manuscript `.md` files are outside every rule. **`meta-analysis.md` is one of them.**

3. **The only consumers of `research/meta/results.json` in the tracked corpus are the module that writes it and one prose line of the manuscript** (`grep -rn "meta/results.json"` → `meta-analysis.mjs:8,105` and `meta-analysis.md:139`). Combined with W30c's measured "no gate runs this module", the DL figures in the manuscript are unpinned, unlinted and unregenerated by any gate.

### D. One measured discrepancy, reported not repaired (PRIMARY)

`meta-analysis.md:136` prints the disease-specific-mortality crude cell as **`14% (n=266)`**. The crude denominator for that pool, summed from the committed registry via `results.json`, is **262** (Masunaga 134 + 29 = 163, Meis-Kindblom 99). **266 − 262 = 4, and the source of the 4 is UNKNOWN** — no cohort in the registry with a `diseaseDeath` block carries a denominator that closes the gap. The percentage itself is correct (36/262 = 13.74% → 14%). This is the one place in the file where a printed quantity does not reconcile with either method's arithmetic; it is a denominator label, not an estimate, and it changes no interval. I have authored no correction and propose none here.

**No clinical claim is made or restated.** Every figure above is a pooled descriptive proportion from published retrospective series, hypothesis-generating by POLICY-evidence §2's own wording, and carries §2.5's limitations in full: publication bias, heterogeneous and often short follow-up, no censoring or Kaplan–Meier, no risk adjustment or multivariable control, small total N. Nothing here says any treatment works, is safe, or is ready for a patient, and none of it is a prognosis for any individual. There is no wet lab.

## Validation evidence

**RUN.** Environment: `/home/user/Rare-cancers`, HEAD `56f355f6` → `fcb36d3c`. `git` 2.x, system `python3` (stdlib only), `grep`. No `node` invoked.

Independent crude+Wilson recomputation (heredoc, `cwd=/tmp/claude-0/w68`, reading the repo by absolute path, writing nothing), verbatim output:
```
recurrence: sum 88/326 crude 26.99% Wilson (22.46-32.06)  || DL 27.84% (14.21-47.34) I2=90.4
   studies: [('Masunaga 2025', 16, 134), ('Meis-Kindblom 1999', 40, 83), ('US Sarcoma Collaborative 2022', 18, 60), ('Chiusole 2020', 14, 49)]
metastasis: sum 94/259 crude 36.29% Wilson (30.68-42.31)  || DL 37.90% (27.48-49.58) I2=69.1
   studies: [('Masunaga 2025', 39, 134), ('Meis-Kindblom 1999', 35, 76), ('Chiusole 2020', 20, 49)]
diseaseDeath: sum 36/262 crude 13.74% Wilson (10.09-18.44)  || DL 14.19% (8.55-22.63) I2=61.6
   studies: [('Masunaga 2025', 18, 163), ('Meis-Kindblom 1999', 18, 99)]
```

`pinned-figures.json` census, verbatim output:
```
'POLICY-evidence' 0
'§2.2' 2
'emc-clinical-registry' 0
'endpoint/' 19
'meta' 0
```
and, from the earlier keyword pass: `meta-analysis 0 / results.json 0 / locoregional 0 / recurrence 0 / metasta 0 / diseaseDeath 0 / Wilson 3 / wilson 2 / DerSimonian 0`. `targets` is a 29-element list of strings; `research/manuscripts/endpoint/meta-analysis.md` is absent from it (full list printed in the transcript).

Consumers of the artifact, verbatim:
```
./research/meta/meta-analysis.mjs:8:// Outputs: console summary + research/meta/results.json (study-level data). …
./research/meta/meta-analysis.mjs:105:console.log("Results: research/meta/results.json");
./research/manuscripts/endpoint/meta-analysis.md:139:`research/meta/results.json`):
```

Write-isolation close-out:
```
$ rm -rf /tmp/claude-0/w68 && ls /tmp/claude-0/w68
ls: cannot access '/tmp/claude-0/w68': No such file or directory
$ git status --porcelain      (empty)
```

**PROPOSED (NOT RUN).** I ran no test suite and no gate. `python3 research/manuscripts/lint_consistency.py` would be the natural check of claim 2 by execution rather than by reading the JSON, but its verdict is already known from W51/W44 (`0 ERROR across 29 target file(s)`) and it cannot reach `meta-analysis.md` at all, which is the finding — running it would add nothing. I assert no pass or fail for it. I did not run `meta-analysis.mjs`, `validate-registry.mjs`, `preflight.sh`, or any pytest.

## Limitations

1. **A grep census bounds what I looked for, not what exists.** I searched literal digit strings, `k`/`n` fractions, and pooled-outcome prose across 7,600 tracked files; a pooled figure written only in words ("about a quarter of patients"), inside a binary or `.eps` artifact, or in a rendered figure image would not have been found. Absence in my table is **UNKNOWN for those forms**, not proof of absence.
2. **The DL/crude classification of a whole-percent figure rests on the accompanying interval, not the point estimate.** 28% is compatible with both methods to the printed precision; it is the `14–47%` and `I²=90%` beside it that identify it as DL, and `27% (22–32%)` that identifies the other column as crude+Wilson. Where an interval is absent (the bare `14%` of disease-specific mortality in §4, and `12% vs 28%` in §3.3), my assignment is from the surrounding sentence's stated method, which is weaker evidence than arithmetic.
3. **I did not verify that `results.json` is current with respect to the registry** — W53 established it regenerates byte-identically at an earlier HEAD, and I took that as given rather than re-running the module. If the registry has changed since, the manuscript's printed figures and my crude column would both be stale in the same direction.
4. **`n=266` is a measured non-reconciliation whose cause I did not establish.** I did not search Git history for an earlier registry state that would produce it, and the campaign brief records the history as squashed.
5. **I read only the tracked working tree**, not the frozen corpus at `/tmp/claude-0/frozen-corpus/`. For this question the live tree is the right one (the manuscript and `pinned-figures.json` are both live-tree artifacts, and W38b's line-shift warning applies to two files I did not cite), but a figure present only in the corpus snapshot would be UNKNOWN to me.
6. **No clinical inference.** §2.5's limitations attach to every number quoted above, and nothing here supports a statement about efficacy, safety, selectivity, prognosis or readiness.

## Stop condition

**Set up front:** locate every place in the tracked corpus (excluding the campaign directory) that states a pooled EMC recurrence, metastasis or disease-specific-death figure; classify each against both computations; and determine by direct inspection whether any `pinned-figures.json` entry pins one of them and which artifact/key it reads — then return without changing anything.

**MET.** Ten locations tabulated across four files plus four method-only documents; every one classified DL, crude+Wilson, or both; `pinned-figures.json` measured to pin **none** of them (0 occurrences of every relevant key; `meta-analysis.md` absent from its 29 targets); the cross-method mis-citation the dispatch asked about **does not exist in the committed corpus**; one incidental denominator discrepancy (`n=266` vs 262) recorded. No repair authored.

## Tool-call and wall-clock count actually used

**16 tool calls** (14 Bash, 2 Read; two issued in parallel twice), of which 2 were the mandated start/end state records. **0** network calls, **0** MCP calls, **0** repository writes, **0** git write operations, **0** executions of `meta-analysis.mjs` anywhere. Wall clock **04:51:31Z → 04:54:37Z ≈ 3.1 minutes** of measured tool time plus report drafting. Well inside the ~40/~40 target; returning rather than padding.

## Next concrete action

**One successor, and it is a question for the manuscript's owner rather than another audit.** The measurement is now complete on both halves of W53's successor question, and the answer is largely reassuring: the corpus quotes the two methods correctly wherever it quotes them, and `emc-locoregional-eligibility.json` is a model of how (it names its estimator, its § numbers, and the pooler it deliberately did **not** use). What remains is not a defect to fix but a **coverage gap to decide about**: `research/manuscripts/endpoint/meta-analysis.md` prints eighteen pooled quantities, is read by no gate, no test and no `pinned-figures.json` entry, and its own header says *"Numbers current as of the last data build — regenerate before any version is circulated"* with nothing that can tell anyone whether that was done. The concrete, bounded, non-scientific successor is: **add `research/manuscripts/endpoint/meta-analysis.md` to `pinned-figures.json`'s targets with entries pinning the three DL headlines and the three crude/Wilson cells to `research/meta/results.json`, so `lint_consistency.py` catches a drift between the manuscript and the artifact it names.** That is a repository-owner decision (it changes a shipped registry and a gate's scope), it must not be taken by a campaign worker, and it should be paired with a human ruling on the `n=266` cell, which any such pin would immediately turn red. I propose it; **I have written nothing into the repository, authored no repair, proposed no patch as code, added no gate row and changed no guard.** W53's, W30c's and W30d's open proposals stand unaddressed by me.
