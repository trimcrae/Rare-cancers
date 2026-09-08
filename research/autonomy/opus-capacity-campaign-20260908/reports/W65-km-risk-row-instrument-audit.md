<!-- collected 2026-09-08T04:54:43Z by campaign coordinator; agent id ab2055d41725fae9e; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ab2055d41725fae9e.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

W65, OPUS-CAPACITY-CAMPAIGN-20260908. Instrument-audit lane (`research/modalities/km_risk_row_detect.py`).

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED — Claude Opus 5 (`claude-opus-5`).** The environment carries no model variable; the coordinator must extract the served model from the transcript.

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

**Start:** `date -u` = `Tue Sep  8 04:48:54 UTC 2026`; `git rev-parse HEAD` = `8a667406e875ae99c7d50347b2e895a177fcb048`; `git status --porcelain` = **empty**.
**End:** `date -u` = `Tue Sep  8 04:50:16 UTC 2026`; `git rev-parse HEAD` = `461328470aa6920447c0b9f372ee7fa0085cfd0a`; `git status --porcelain` = **empty**.

HEAD advanced mid-run (coordinator commits collecting sibling reports — six untracked `reports/W*.md` files appeared in a mid-run `git status` and were committed by the coordinator before my end check). None of them are mine. I wrote nothing into `/home/user/Rare-cancers`, ran no git write operation, and deleted my scratch (`rm -rf /tmp/claude-0/w65 /tmp/claude-0/w65_check.json /tmp/claude-0/w65_check.err`).

## Question

Audit `research/modalities/km_risk_row_detect.py` on its own terms: (a) what it actually measures and what `present`/`absent`/`undetermined` mean; (b) whether the recorded claim in `emc_ipd_survival.py:220-228` — that instrument and eye agree on all nine Kaplan-Meier figures, and that the instrument fires on the two figures that do print a risk row — holds against the committed artifact and a fresh control run; (c) what the instrument does not establish. Open because W43 cited this as the repository's own precedent for the unread-act-assertion class without anyone re-running the instrument or checking the agreement claim figure-by-figure.

## Prior-work check

```
rg -n -l "km_risk_row_detect" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'
```
→ 9 files: `systems/views/L2-rt-ipd-survival.md`, `systems/graph/routes.json`, `research/modalities/emc_ipd_survival.py`, `research/autonomy/receipts/CYC-0023.json`, `research/autonomy/research-ledger.json`, `research/modalities/emc-ipd-survival.json`, `research/modalities/km-risk-row-detection.json`, `research/modalities/tests/test_km_risk_row_detect.py`, `research/modalities/km_risk_row_detect.py`.

```
git ls-files | rg -i "km_risk|km-risk|km_digit|km-figure|km-swimmer|km-admiss"
```
→ `research/literature/emc-km-admissibility-2026-08-27.json`, `research/literature/emc-km-figure-retrieval-2026-08-25.json`, `research/modalities/km-figure-readings.json`, `research/modalities/km-risk-row-detection.json`, `research/modalities/km-swimmer-readings.json`, `research/modalities/km_digitize.py`, `research/modalities/km_risk_row_detect.py`, `research/modalities/tests/{test_km_digitize.py,test_km_risk_row_detect.py}`.

No prior worker-facing audit of the instrument exists in the tracked corpus; the artifact and its 16 tests exist but nobody has cross-tabulated the two readings. Confirmed I am not replaying anything in `CLOSED-WORK.md`: I retrieved no figure, no paper, no denied route; the unrecovered sources (pazopanib, sunitinib 2014, CTARC, Wagner) are untouched. I took W43's 34-field census as given and did not re-census.

## Method and inputs

Files read in full: `research/modalities/km_risk_row_detect.py` (886 lines), the five `figure_checked: True` rows of `research/modalities/emc_ipd_survival.py` (lines 200–406), `research/modalities/km-risk-row-detection.json` (the committed measurement), `research/modalities/tests/test_km_risk_row_detect.py`, `systems/POLICY-evidence.md` §2.7, and the three campaign context files.

Write-site check before executing anything: `main()` at `km_risk_row_detect.py:869-886` — under `--check` it calls `run_control()`, `print(json.dumps(...))` and returns; the only `open(..., "w")` is at `:882`, on the `--pdf-dir` branch. The module-level import `from km_digitize import Image, read_png, write_png` (`:78`) pulls a module whose writes are all inside functions. So `--check` is read-only, and I ran it in the live tree.

Environment: Python 3.11.15, pytest 9.1.1 (`/root/.local/bin/pytest`; `python3 -m pytest` is the wrong interpreter here per the brief). No network, no paid API, no GPU.

## Result

### (a) What the instrument measures

It measures **band structure in the region beneath a figure's x-axis**, and nothing lexical. The pipeline is: find the bottom-most long horizontal *rule* (`find_axis_row`, threshold `RULE_LUMA_MAX = 235`, span ≥ `AXIS_MIN_SPAN = 0.45` of width, longest *contiguous* run, not ink count); collect ink clusters below it inside the axis's own x-range (`pixel_tokens`, `INK_LUMA_MAX = 170`); group them into horizontal bands (`_bands`); take as the tick-label reference the first band that is *glyph-shaped* (≥ `MIN_MARKS = 3` marks, median width ≥ `MIN_GLYPH_WIDTH = 0.004` of width — this exists because drawn tick marks otherwise occupy band 0); then test each band below it. A band is a numbers-at-risk row iff it has ≥ `MIN_MARKS = 3` marks, ≥ `MIN_MATCHED_TICKS = 3` of them within `TICK_TOL = 0.020` of the width of a tick-label centre, median mark width ≤ `MAX_MARK_WIDTH = 0.055` of width, and it sits within `MAX_RISK_GAP = 0.25` of the figure height below the tick labels. Constants are fractions of figure width/height, so the rule is dpi-independent. Two arms produce the same `Token` shape: **pixel** (embedded raster; positions readable, values not) and **text** (PDF text layer of a vector figure; values also readable, and reported as `risk_row_text`).

The three verdicts, exactly as the code defines them:

| Verdict | Code condition | Meaning |
|---|---|---|
| `present` | a band below the tick labels satisfies count + tick-alignment + narrowness + proximity | **A risk row is printed on this figure image.** That is §2.7(a)'s condition and only that condition — not how many timepoints, not legibility, not whether the cohort is EMC, not poolability (`km_risk_row_detect.py:41-44`). |
| `absent` | tick-label band found, no band below it qualifies, and no at-risk label phrase on the page | **No tick-aligned narrow band beneath this figure's axis.** Scoped to *this figure image*: the paper may print the table in a separate table, a supplement, or prose (`:46-49`). |
| `undetermined` | fewer than `MIN_MARKS` tokens; or no glyph-shaped band; or the first glyph band sits > `MAX_TICK_GAP = 0.10` of the height below the candidate rule (the swimmer-plot/bar failure); or the embedded image encoding is undecodable (DCT/JPX/CCITT, or non-8-bit); or an at-risk *label phrase* is on the page while no aligned band was recovered (a declared conflict, `:214-219`) | **The question was not answered.** Explicitly not a negative: "a missing reading is not a reading of absence". |

The design record is unusually candid about its own near-misses, each dated 2026-08-27 and each still visible as a constant or a control case: a grey axis (`masunaga2025`) that a single luma threshold silently dropped; a swimmer plot (`martinbroto2020`) where a bar was read as the axis and bar-ends as a risk row; drawn tick marks read as the risk row on `masunaga2025` Fig. 3; and, in the text arm, two rejected anchors (no anchor → a "risk row" on 26 of 29 figures including title pages; longest drawn rule → a table footnote read as a risk row).

### (b) Agreement — the nine Kaplan-Meier figures

The committed artifact holds **15 figure rows across 5 papers** (`_totals`: papers 5, figures 15, with_risk_row 2, without 9, undetermined 4). The **nine KM figures** are the subset the human reading declares in `emc_ipd_survival.py` `figure_finding.km_figures` (3 + 4 + 0 + 1 + 1); the other six rows are non-KM graphics on the same pages. Both readings, per figure:

| # | Source (n) | Figure | Human reading (`figure_finding`, 2026-08-25) | Instrument verdict (2026-08-27) | Arm / input | matched ticks | Agree | Class |
|---|---|---|---|---|---|---|---|---|
| 1 | masunaga2025 (171) | Fig. 1 DSS by distant mets at dx | `numbers_at_risk_row: False` | `absent` | pixel / embedded raster | 0 | ✔ | PRIMARY (graphic) |
| 2 | masunaga2025 | Fig. 2 LRFS by (neo)adjuvant RT | `False` | `absent` | pixel / embedded | 0 | ✔ | PRIMARY |
| 3 | masunaga2025 | Fig. 3 DSS by advanced-stage chemo | `False` | `absent` | pixel / embedded | 0 | ✔ | PRIMARY |
| 4 | chiusole2020 (59) | Figure 1 OS by extent of primary resection | `False` | `absent` | pixel / **page raster** | 0 | ✔ | PRIMARY (weaker input) |
| 5 | chiusole2020 | Figure 2 OS by sex | `False` | `absent` | pixel / page raster | 0 | ✔ | PRIMARY (weaker input) |
| 6 | chiusole2020 | Figure 3 OS by primary location | `False` | `absent` | pixel / page raster | 0 | ✔ | PRIMARY (weaker input) |
| 7 | chiusole2020 | Figure 4 OS by site of metastases | `False` | `absent` | pixel / page raster | 0 | ✔ | PRIMARY (weaker input) |
| 8 | stacchiotti2013anthracycline (11) | Figure 2 overall PFS | `numbers_at_risk_row: True` | **`present`** | pixel / embedded | **5** (all five tick labels) | ✔ | PRIMARY, positive control |
| 9 | morioka2016trabectedin (5) | Fig. 1 KM plot of PFS, two arms | `True` | **`present`** | **text** / vector | **8** | ✔ | PRIMARY, positive control |

**Agreement: 9 / 9.** Present 2, absent 7, undetermined 0 among the nine. The recorded claim holds.

**Positive-control result — the instrument demonstrably returns the other answer.** Both `present` verdicts are on real papers, not synthetics: `stacchiotti2013anthracycline` p5 (band index 3, five marks aligned with all five tick labels, pixel arm — values not readable by design) and `morioka2016trabectedin` p4 (band index 3, eight matched ticks, text arm). The text arm additionally recovered the row's **values**: `['Trabectedin','5','5','5','3','3','1','1','1']` against tick row `['0','3','6','9','12','15','18','21','24']`. Those eight numbers are byte-identical to the eye reading transcribed two days earlier in `figure_finding.risk_table_printed.trabectedin` = `[[0,5],[3,5],[6,5],[9,3],[12,3],[15,1],[18,1],[21,1]]`. That is an independent second reading of the same eight values by a different method — the strongest single row in this audit.

The six non-KM rows, for completeness (they are correctly outside the nine, and the human field for the one paper among them records `numbers_at_risk_row: None`, i.e. not a claim):

| Source | Row | Verdict | Note |
|---|---|---|---|
| martinbroto2020immunosarc1 | p6 "Figure 3 PFS by patient" | `absent` | a **swimmer plot**, `km_figures: 0`; the human row says the verdict "means less here", and `km-swimmer-readings.json` is the right instrument |
| masunaga2025 | p11 "Supplementary Information" | `undetermined` | not a KM figure |
| morioka2016 | p1 journal header banner | `undetermined` | not a figure |
| morioka2016 | p5 "Fig. 2 Clinical course… CT images" | `undetermined` | CT panel |
| morioka2016 | p6 "Fig. 3 Clinical course… CT images" | `absent` | CT panel |
| morioka2016 | p8 page footer | `undetermined` | not a figure |

**Fresh control run (8/8 separations reproduced, exit 0):**

| Case | Expected | Got | Bands | Matched |
|---|---|---|---|---|
| plain_no_risk_row | absent | absent | 2 | 0 |
| risk_row_present | present | present | 3 | 6 |
| misaligned_band | absent | absent | 3 | 0 |
| wide_marks_band | absent | absent | 3 | 0 |
| tick_marks_no_risk_row | absent | absent | 3 | 0 |
| tick_marks_with_risk_row | present | present | 4 | 6 |
| tick_labels_far_below | undetermined | undetermined | 0 | 0 |
| aligned_band_far_below | absent | absent | 3 | 0 |

Identical to the `control` block frozen inside `km-risk-row-detection.json` (`passed: true`, same 8 cases, same expectations, same verdicts). The two mutations that would make a structural rule useless — a band that is not tick-aligned (an axis title) and a tick-aligned band of *wide* marks (a row of words) — both correctly fail to fire, and both directions of the swimmer-plot failure are pinned.

### (c) What the instrument does **not** establish

It measures a **graphical feature of a figure image**: whether a narrow, tick-aligned band of marks is printed beneath the axis. It says nothing whatever about whether any digitized coordinate is correct. The pixel arm does not read glyphs at all — a `present` verdict there is "a row of unknown values is printed"; the values are read separately, by eye, through `km_digitize.py`, which is where digitization provenance (§2.7(c)) lives. `present` is §2.7(a)'s admissibility condition only: not timepoint count, not legibility, not that the cohort is EMC, not §2.1/§2.3 poolability. `absent` is about the image this ran on, not about the paper. And the synthetic control draws **blocks, not glyphs**, so it bounds the structural rule alone — its own artifact says it is "structurally incapable of failing on a real figure that is hard to read", the same limit `POLICY-evidence.md` §2.7 records for the reconstruction's known-answer control (⛔ clause). Nothing here is a statement about survival, efficacy, safety, selectivity or clinical readiness.

## Validation evidence

**RUN** (cwd `/home/user/Rare-cancers`, Python 3.11.15, pytest 9.1.1, no network):

1. `python3 research/modalities/km_risk_row_detect.py --check` → **exit 0**, stderr empty, `"passed": true`, 8/8 cases as tabled above. Write-free path confirmed by source read of `main()` before execution; `git status --porcelain` immediately after showed only coordinator-authored untracked `reports/W*.md`, no modification to any tracked file.
2. `pytest research/modalities/tests/test_km_risk_row_detect.py -q` → `................  [100%]` / `16 passed in 1.96s`, **exit 0**. These 16 include a genuine anti-vacuity test (`test_the_control_is_capable_of_failing`), the grey-axis and bottom-most-axis regressions, and four artifact-integrity tests asserting every verdict is in the closed set, every source carries a sha256, and no unreadable figure is recorded as a negative.
3. Cross-tabulation of the nine rows above: read directly from `research/modalities/km-risk-row-detection.json` (instrument) and `research/modalities/emc_ipd_survival.py:252-406` (`figure_finding` / `risk_row_measured_2026_08_27`), parsed with `python3 -c` over the JSON; no value retyped from memory.

**PROPOSED (NOT RUN)** — re-running the real-figure arm (`--pdf-dir`). Not run, and **not runnable at this HEAD**: the figures are deliberately uncommitted (licence), and the artifact's `inputs` names `cache_branch: origin/literature-cache`, `cache_path: literature/km-figures-2026-08-25/`, `cache_commit: 454df71144f677b1e84ed58f7a6c6951a4190f66`, with page rasters from `pdftoppm -r 200 -png` in Actions run 32903796837. Per the campaign brief (W40, measured), `origin/literature-cache` has never existed in this checkout. I did not fetch, and no retrieval is authorised.

## Limitations

- Part (b) verifies the recorded claim **against the committed artifact and a reproduced control**, not by re-reading the PDFs. The nine real-figure verdicts are as-recorded; their inputs' sha256 digests are stated in the artifact but **unverifiable at this HEAD**, since the PDFs are not present and the cache ref does not resolve here. If the instrument were ever re-run on different files, this audit would not detect it.
- The partition "which 15 rows are the nine KM figures" is **human-supplied** (`figure_finding.km_figures` plus caption text); the instrument does not classify figure type. So the agreement statistic inherits one human classification step — though the captions in the artifact (`caption_head`) independently corroborate it for all nine.
- Four of the nine (`chiusole2020`) were measured on a **page raster**, a resampled copy, because that paper stores its curves as JPEG which the pure-stdlib decoder declines. The artifact labels these `source: page_raster` and the human row flags it. A small-type risk row is closer to the resolution floor there than in the publisher's own image, so those four `absent` verdicts rest on the weaker input.
- The pixel arm's `present` verdicts carry no values. Agreement on figure #8 is agreement about a *graphic*, not about the five numbers in that risk table; only figure #9 has two independent value readings.
- Nothing in this report bears on survival, efficacy, safety, selectivity or clinical readiness, and no number from any reconstructed curve is restated as a clinical claim. §2.7's own ⛔ stands: a passing control on an algorithm is not evidence about any particular curve.
- I did not test the instrument's constants for sensitivity, did not extend it to any other field, and authored no repair, patch, gate or test. No guard was weakened, relaxed or reordered. No content-policy refusal was encountered.

## Stop condition

Set up front: **stop as soon as (i) the instrument is read in full and its three verdicts are stated from its code, (ii) the nine-figure agreement table is built from both recorded readings with a count, (iii) the positive-control claim is checked against the artifact, and (iv) the control is reproduced by a verified write-free execution.** All four met. Stopping now; nothing padded.

## Tool-call and wall-clock count actually used

**19 tool calls** (all Bash; several issued in parallel blocks). Wall clock from first to last recorded timestamp: `04:48:54Z` → `04:50:16Z`, **≈1.4 minutes of tool time**, well inside the ~40-call / ~40-minute target. Scratch deleted; live tree verified untouched.

## Next concrete action

One specific successor, and it needs no new instrument and no retrieval: **the artifact's re-derivability claim is the only untested clause in this file.** `km_risk_row_detect.py:52-55` and the artifact's `⛔_the_figures_are_not_committed` key stake the whole measurement on "the recipe: the branch and path every PDF was read from, and the sha256 of each file as read." At this HEAD that recipe **does not resolve** — `origin/literature-cache` is absent from the checkout (W40, measured), so the five recorded digests cannot be matched against anything. `test_the_inputs_are_named_well_enough_to_re_derive` asserts the fields are *populated*, not that they *resolve*. The concrete task is to determine, without fetching, whether `cache_commit 454df71144f677b1e84ed58f7a6c6951a4190f66` is reachable from anything in this repository's object store or from the Actions run record, and to record the answer as ENFORCED / UNDECIDABLE — because if it is undecidable, then this instrument, which exists precisely to make an unfalsifiable JSON field falsifiable, currently rests on an input provenance record that is itself unfalsifiable here. That is a real and bounded question, it is in this lane, and it is the honest limit of what I could check.
