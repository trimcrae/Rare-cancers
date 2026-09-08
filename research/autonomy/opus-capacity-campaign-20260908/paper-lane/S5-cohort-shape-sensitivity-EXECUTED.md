<!-- collected 2026-09-08T06:26:38Z by campaign coordinator; agent id a53b0d25fa5e70b56; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a53b0d25fa5e70b56.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**S5**, OPUS-CAPACITY-CAMPAIGN-20260908, paper-lane (synthetic instrument method-development).

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED — `claude-opus-5`.** No environment variable names a served model; the coordinator must extract the actual runtime model from the transcript.

Start `date -u` = `Tue Sep  8 06:19:12 UTC 2026`; end `date -u` = `Tue Sep  8 06:22:24 UTC 2026`.
Start HEAD `c75244f975dec73927d7e0d23a9f54edf55c3855`, `git status --porcelain` empty.
End HEAD `ae6315c49594f97a18cd7e6d8f040bcf9003ee61` (the parent's own commit `paper-lane: S5 durable location moved outside the checkout, in flight` — it advanced under me and it also committed my checkout files), `git status --porcelain` empty. Disk `/` = **20 GiB avail at both ends** (floor 10 GiB honoured). I ran **no git operation of any kind**.

Literal start-of-run env grep (redacted per instruction):

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...(same list)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy config)
NO_PROXY=localhost,127.0.0.1,::1,...(same list)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...(same list)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

End-of-run grep re-checked; the identity-relevant lines are unchanged (`AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_CODE_VERSION=2.1.42`, `CLAUDE_EFFORT=medium`, `ANTHROPIC_BASE_URL=https://api.anthropic.com`).

## Question

Do S4's two findings — **extent dominates censored recovery**, and **density is non-monotone with the read arm degrading past ~5 rows** — persist across prespecified, structurally distinct censoring shapes, and does controlled variation in rendering or reading settings change the ranking of those effects?

S4's own proposed successor (repeat `render_km` per cell to build a "distribution") was **rejected in my contract and NOT run**: `render_km` is deterministic, so an identical repeated render is a deterministic repeat, not an independent draw. I varied cohort shape and fixed render/read scenarios instead.

## Prior-work check

```
rg -n -i "cohort.shape sensitivity|censoring shape|shape sensitivity" --glob '!.git' \
   --glob '!research/autonomy/opus-capacity-campaign-20260908/**' | head -20   -> 0 hits
git ls-files | rg -i "km_digitize|ipd_survival"
   -> research/modalities/emc_ipd_survival.py
      research/modalities/km_digitize.py
      research/modalities/tests/test_emc_ipd_survival.py
      research/modalities/tests/test_km_digitize.py
```

No tracked repository file addresses cohort-shape sensitivity of the risk-table density/extent effect. `km_digitize.cohort_size_sensitivity()` varies **n**, not censoring **placement**, and holds the risk table at the committed 8-row grid. I read `CLOSED-WORK.md`: I am replaying no closed gate, recreating no held review, touching no W25/GSE243553/primary-article/Results/novelty/NR4A item, and re-running nothing to recreate S4's lost `out.json`/`out2.json` or their timing fields.

## Method and inputs

`research/modalities/km_digitize.py` and `emc_ipd_survival.py` imported **unmodified** from the repository (sys.path insert; no copy edited). All three contract pins verified at run time and **all three match**:

| input | sha256 | pin match |
|---|---|---|
| `research/modalities/km_digitize.py` | `05aeeb4b8f2150f65cf95d8320c0f5dac647f928a42ed2ebba40276ae1a7dd37` | yes |
| `research/modalities/emc_ipd_survival.py` | `a82420f026547a27d5dbe571faa8325bdf4fd1930281eec163db2c20157f5aa5` | yes |
| `paper-lane/S4-executed-artifacts/sweep.py` (reused, not rewritten) | `28aa8e7c1cf17278d935986c1d6b6d934feafd05a03e1fea743d4356d81fd47d` | yes |

`sweep5.py` is S4's `sweep.py` with the cell/arm machinery (`reconstruct_cell`, `risk_table_from_times`, `uniform`, the crash-is-a-result `except`) carried over verbatim; only the outer loops changed.

**Thresholds imported and echoed, never modified anywhere including scratch:** `MAX_KM_DEVIATION_as_imported = 0.05`, `REQUIRE_RISK_TABLE_as_imported = true`.

**Randomness: DETERMINISTIC, NO SEED IS USED.** No randomness is consumed. `km_digitize._synthetic_cohort` constructs `_Rng(90210 + n)` but never samples from it (`_ = rng`); the other two cohorts are written out arithmetically. This is **measured, not asserted**: each cohort was re-derived twice in-process and compared by canonical-JSON sha256 — **4 of 4 identical** (`meta.determinism_selfcheck`).

**Vocabulary, held throughout:** every arm is a **fixed prespecified scenario**. Nothing below is a distribution, replication, draw, variability or confidence, and no statistic presupposing sampling was computed.

## Cohort shapes and their truth

All four are synthetic generated arithmetic. **No row is a patient.**

| cohort | construction | canonical sha256 | n | events | censored | truth median | min/max t | last obs is event | n at t_max |
|---|---|---|---|---|---|---|---|---|---|
| `emc_anchor__terminal_censoring` | `kd._emc_shaped_cohort()` (S4's cohort) | `7deb0b9f61a765f83d8b3585b9d0e47f04da9c0788205f73b1caf71cb94deea9` | 59 | 18 | 41 | 168.0 | 3.0 / 180.0 | no | **5** |
| `early_censoring` | explicit arithmetic: censor 2,4,…,82; events 84,89,…,169 | `524fab9ed618d9274039bfb1d8a47820d2b7f07ad5a99280dd583977c6fc1eab` | 59 | 18 | 41 | 124.0 | 2.0 / 169.0 | **yes** | 0 |
| `uniform_censoring` | `kd._synthetic_cohort(59, 0.30, 180.0)` | `3ca5af0e5ef9fb2c0df6f49a0393fedf0a06c1abe2f7be36c9d20dca510e5e87` | 59 | 17 | 42 | 157.1 | 5.4 / 174.6 | no | 0 |
| `low_event` | `kd._synthetic_cohort(59, 0.10, 180.0)` | `44f23fd9e19864252899395dcbbb7f237ea7101dc5599ae3f5f6e072825cd694` | 59 | **6** | 53 | **None (not reached)** | 5.4 / 174.6 | no | 0 |

The anchor's cohort hash `7deb0b9f…` is **byte-identical to the value S4 recorded**, so the two grids are directly comparable.

## The grid actually run (and what was dropped)

- **Density axis:** rows **3, 5, 8, 13, 19** at fixed extent 0.933 (last row 168.0) — spans S4's non-monotone region with ≤5 and ≥13 present.
- **Extent axis:** **0.25, 0.50, 0.75, 0.933, 1.00** at fixed density 8 rows.
- **Render/read scenarios (4, all Pillow-free):** `clean__strict_matcher`; `line_width_4__strict_matcher` (`render_km(line_width=4)`); `gridlines__strict_matcher` (`render_km(gridlines=True)`); `clean__lenient_matcher_luma175` (`dark_matcher(max_luma=175)`).
- **Control:** an **exact-coordinate arm in every cell** (no render, no read).
- **Totals: 4 cohorts × 10 cells = 40 cells; 40 × (1 exact + 4 read) = 200 reconstructions.** No cell was dropped.
- **Dropped from S4's design on purpose:** rows 2 and 25, extent axis 2b (S4 already labelled it confounded), and the whole anchoring axis 3 — S5's question is about the two directional claims, and axis 3's answer (a one-patient effect) does not bear on them. Row spacing is not independently controllable at fixed extent or fixed density; that confound is inherited from S4 and is stated, not hidden.

**Why this finite grid answers the question:** the two S4 findings are *directional* claims about how error moves with rows and with extent. Re-measuring the same two directions on cohorts whose censoring sits somewhere else either reproduces the direction — evidence it is a property of the instrument — or does not — evidence it was a property of that one cohort. Adding grid points refines a magnitude; it cannot change which of those two the answer is. Four shapes × two directions × four fixed read scenarios is the smallest grid that separates them and also tests whether a render/read setting reorders them.

## Durable artifacts written and verified

**Primary durable location (per the coordinator's mid-task change):** `/tmp/claude-0/s5-retained/` — created, populated, **verified, and NOT deleted**.

```
sha256sum -c SHA256SUMS.txt
MANIFEST.md: OK
sweep5.py: OK
summarize5.py: OK
results.json: OK
SUMMARY-TABLES.txt: OK
RUNLOG.txt: OK
stderr.txt: OK
```

| file | bytes | sha256 |
|---|---:|---|
| `MANIFEST.md` | 5,098* | `04c1a4aff4f0da24ac9b036f36c9d6641d8cf54521ded8b9ba2cf3839f7d5fd3` |
| `sweep5.py` (exact executed code) | 13,012 | `469222f686a6d9177ba8da935f67ac6e46eff3670b1d7f77eb1c0d5aa4d3b91a` |
| `summarize5.py` | 1,999 | `40d5dbe77d02985812adb2abce3794a580260a7d62cda38d159bb5148c90d125` |
| `results.json` (**raw, all 40 cells × 5 arms, unabridged**) | 126,998 | `4a465b1a41e4b1812c71fee68fa37b6d305f2521e3717da87c5ba65556c51ef5` |
| `SUMMARY-TABLES.txt` | 19,621 | `ffec705e332205733d7fae8b28cc71d619c064d33ba3b84ff75fbdce47b89fef` |
| `RUNLOG.txt` (timing, exit code — **original bytes**) | 183 | `d0ae39c82d05b7aac701c14cab902092ba1379dcd0a8ed151d795e13d9316853` |
| `stderr.txt` (empty, as produced) | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `SHA256SUMS.txt` | 552 | `5eedaac191311511cd918b5c9a132874d9117e822333df10fc68e21d53518cbb` |

\*`MANIFEST.md` was edited once after its first hash to correct a garbled refusal count; `SHA256SUMS.txt` was regenerated and re-verified after the edit. The hash above is the final one.

**Files left in the repository checkout** at `research/autonomy/opus-capacity-campaign-20260908/paper-lane/S5-executed-artifacts/`, written **before** the coordinator's location change and **left exactly as they are** (not deleted, moved or rewritten): `sweep5.py`, `summarize5.py`, `results.json`, `SUMMARY-TABLES.txt`, `RUNLOG.txt`, `stderr.txt` — **byte-identical, same sha256 as the table above**. The parent has already committed them (`ae6315c4`), which is why `git status --porcelain` is empty at end. No `MANIFEST.md`/`SHA256SUMS.txt` was written into the checkout.

**No scratch was deleted**, because I created none outside these two locations. Verification passed before any cleanup would have occurred.

## Per-cell results

Deltas are reconstruction − truth. `maxdev` = `internal_max_abs_km_deviation` against the **unmodified** floor 0.05. Full unabridged per-cell output including `n_reconstructed`, per-cell `seconds`, risk tables and risk times is in `results.json`; the complete printed grid is `SUMMARY-TABLES.txt`.

### Read-scenario identity check (a genuine null)

`gridlines__strict_matcher` and `clean__lenient_matcher_luma175` produced **byte-identical digitized series to `clean__strict_matcher` in all four cohorts** (`digitized_sha256` equal, same point counts). Gridlines are drawn at RGB (215,215,215), luma 215, above both the strict (110) and the lenient (175) thresholds, so neither matcher sees them. Every cell of those two scenarios is therefore identical to clean and is reported as such, not as a separate effect.

| cohort | clean pts / sha12 | line_width_4 pts / sha12 | gridlines | lenient |
|---|---|---|---|---|
| emc_anchor | 20 / `48af484b6712` | 38 / `f97c541705ed` | = clean | = clean |
| early_censoring | 20 / `bd61ade32701` | 22 / `0bd5e8b34a86` | = clean | = clean |
| uniform_censoring | 19 / `61568d1773e7` | 36 / `a4a67366849e` | = clean | = clean |
| low_event | 8 / `31cc870fb7f7` | 14 / `db20c9eafd67` | = clean | = clean |

The anchor's clean `digitized_sha256` `48af484b67124d15…` **reproduces S4's recorded value exactly** — an independent recomputation of S4's render/read under me.

### Density axis (extent fixed 0.933) — `censored_delta_vs_truth`

| cohort | arm | rows 3 | 5 | 8 | 13 | 19 |
|---|---|---|---|---|---|---|
| emc_anchor | exact | −7 | −7 | −7 | −7 | −11 |
| emc_anchor | clean read | −10 | −8 | **−15** | **−20** | **−29** |
| emc_anchor | line_width_4 | −9 | −8 | −8 | −9 | −11 |
| early_censoring | exact | 0 | 0 | 0 | 0 | 0 |
| early_censoring | clean read | −1 | **−41** | −35 | −40 | **−41** |
| early_censoring | line_width_4 | −1 | −40 | −36 | −40 | −40 |
| uniform_censoring | exact | −3 | −3 | −3 | −3 | −3 |
| uniform_censoring | clean read | −2 | −2 | −3 | **−18** | **−2** |
| uniform_censoring | line_width_4 | −2 | −2 | −3 | −6 | −2 |
| low_event | exact | −3 | −3 | −3 | −3 | −3 |
| low_event | clean read | −4 | **−30** | **−48** | **−51** | −49 |
| low_event | line_width_4 | −4 | −5 | −4 | −3 | −3 |

### Extent axis (density fixed 8 rows) — `censored_delta_vs_truth`

| cohort | arm | 0.25 | 0.50 | 0.75 | 0.933 | 1.00 |
|---|---|---|---|---|---|---|
| emc_anchor | exact | −25 | −16 | −10 | −7 | **−5** |
| emc_anchor | clean read | −34 | −20 | −15 | −15 | −11 |
| emc_anchor | line_width_4 | −25 | −16 | −10 | −8 | −9 |
| early_censoring | exact | −19 | **0** | 0 | 0 | 0 |
| early_censoring | clean read | −41 | −38 | −38 | −35 | −38 |
| uniform_censoring | exact | −33 | −22 | −11 | **−3** | **−6** |
| uniform_censoring | clean read | −33 | −22 | −22 | −3 | −6 |
| low_event | exact | −42 | −28 | −13 | **−3** | **−6** |
| low_event | clean read | −49 | −51 | −49 | −48 | −48 |

Events deltas on the extent axis run large at short extent and vanish by 0.75–0.933 in every cohort (e.g. `early_censoring` exact `events_delta +19` at 0.25 → 0 from 0.50 on; `uniform_censoring` +11 → +6 → +1 → 0 → 0). Median deltas are in the raw file; the `low_event` truth median is **None (not reached)**, so every median delta there is `None` by construction, not a missing measurement.

## Observed failures

Every failure kept; none dropped, none routed around.

1. **`results.failures` = `[]`** — no render refused (`read["ok"]` true in 16 of 16 renders, `refusal` null in all) and **no exception in any of the 200 reconstructions**. The `except` never fired; `stderr.txt` is 0 bytes; `EXIT=0`.
2. **`assess_quality` refused 11 of 200 arms on the unchanged floor 0.05**, all in read arms, all on the density axis, **0 of 40 exact-coordinate arms refused**:
   - `uniform_censoring` rows 13 — clean 0.0560, gridlines 0.0560, lenient 0.0560 (3 arms), message `['km_deviation 0.056 exceeds floor 0.05']`;
   - `uniform_censoring` rows 19 — clean 0.0548, line_width_4 **0.0641**, gridlines 0.0548, lenient 0.0548 (4 arms);
   - `low_event` rows 3 — clean 0.1015, line_width_4 0.1062, gridlines 0.1015, lenient 0.1015 (4 arms).
   `emc_anchor` and `early_censoring` had **0** refusals. **No guard was touched to make anything pass.**
3. **Missing dependency, named exactly:** Pillow — `python3 -c "import PIL"` → `ModuleNotFoundError: No module named 'PIL'`. Call site `km_digitize.jpeg_roundtrip`, `km_digitize.py:1495-1501`. No scenario in my grid depends on it; that branch is **stopped as unavailable**. Nothing was installed or downloaded.
4. **No content-policy refusal occurred.**
5. **Non-failure worth flagging as a limitation, not a defect:** the `gridlines` and `lenient_matcher` scenarios were *ineffective* — they changed no pixel the matcher sees. Two of my three read variations therefore carry no discriminating information, and only `line_width_4` actually varied the reading.

## Sensitivity across scenarios — what persists and what does not

These are **fixed prespecified scenarios**, not draws; "persists" means the sign of the same directional claim recurs across the four cohort shapes, nothing more.

**Finding 1 — "extent dominates censored recovery": PERSISTS in direction across all four shapes, but not to the endpoint, and not in magnitude.**
In the exact arm, moving the last printed row from 0.25 to 0.933 of `t_max` improved `censored_delta` monotonically in **4 of 4** cohorts (−25→−7, −19→0, −33→−3, −42→−3). But extending further from 0.933 to **1.00 made it worse in 2 of 4** (`uniform_censoring` −3→−6, `low_event` −3→−6), while it helped in `emc_anchor` (−7→−5) and was flat in `early_censoring` (0→0). S4's inference that extent is "necessary but not sufficient" holds; S4's specific ordering with 1.00 best is a property of its cohort's five patients sitting at `t_max`, not of the instrument. Magnitude is entirely shape-dependent: `early_censoring` reaches **exact recovery (0 error)** at 0.50 extent, whereas `emc_anchor` never recovers fully at any extent.

**Finding 2 — "density is non-monotone and the read arm degrades past ~5 rows": PARTIALLY persists, and it is contingent on the render scenario, so the claim as S4 stated it does not generalise.**
- Read-arm degradation with more rows recurs in **3 of 4** cohorts under clean rendering (`emc_anchor` −8→−29 past 5 rows; `early_censoring` −1→−41 past 3; `low_event` −4→−49 past 3), but in **`uniform_censoring` it does not** — that cohort's clean read arm is −2, −2, −3, −18, **−2**: worst at 13 rows and fully recovered at 19, which is non-monotone in the opposite sense and is not a degradation.
- The **exact arm's** density degradation does **not** persist. S4 saw the exact arm worsen at 19–25 rows (−7→−11); in my grid only `emc_anchor` shows that (−7→−11 at 19), while the other three cohorts are **flat at every density** (0,0,0,0,0 / −3,−3,−3,−3,−3 / −3,−3,−3,−3,−3). The exact-coordinate control is essentially insensitive to row count in three of four shapes.
- **The ranking is reordered by a rendering setting.** `line_width_4` — a *degraded* 4-pixel curve — **largely abolished the density degradation** in two cohorts: `emc_anchor` at 19 rows went −29 (clean) → **−11** (thick), and `low_event` at 8/13/19 rows went −48/−51/−49 (clean) → **−4/−3/−3** (thick), i.e. thick-line reading nearly matched the exact arm. The associated observable is point count: the thick render yields 38 vs 20 (anchor) and 14 vs 8 (low_event) digitized points, so the read curve carries more step structure for the recursion. That is a **hypothesis about the mechanism**, not a measured cause; what is measured is that the thick-line render was *better*, not worse, on censored recovery — while simultaneously having a *higher* whole-curve error (`max_abs_curve_error` 0.0612 vs 0.0292 on the anchor). **A render that reads worse by the curve-error metric reconstructed better by the censored-count metric.** So density's effect on the read arm is not a stable property of the instrument: it depends jointly on cohort shape and on line width.
- The other two read variations (gridlines, lenient matcher) changed **nothing**, byte-identical to clean everywhere.

**The internal deviation still fails to police this error class, now across four shapes.** In 189 of 200 arms `internal_max_abs_km_deviation` sat under the unchanged 0.05 floor and `admissible` was True — including `low_event` clean read at 13 rows, which lost **51 of 53 censorings** at `maxdev 0.0225`, and `early_censoring` clean read at 19 rows, which lost **41 of 41** at `maxdev 0.0142`. This reproduces S4's observation on three additional cohort shapes.

## What this does and does not support

Supported, scoped to **these four synthetic cohorts under these fixed scenarios**:

- The extent direction is the more robust of S4's two findings: it recurred in sign in 4 of 4 shapes over 0.25→0.933, though its endpoint behaviour at full-axis extent and its magnitude are cohort-shape properties.
- S4's density finding is the **less** robust: its read-arm form failed in one of four shapes, its exact-arm form failed in three of four, and a single rendering setting (line width 4) removed most of it in two shapes. **On this grid, S4's density claim is better described as a property of that cohort against that render than as a property of the instrument.**
- The admissibility floor does not detect large censored-count loss in any of the four shapes.

Not supported, stated so it cannot be misread:

- **No clinical claim of any kind** — no efficacy, safety, selectivity, prognosis, therapeutic window or readiness for EMC or any disease. The cohorts are generated arithmetic; **no row is a patient**.
- **A passing synthetic cell creates no reporting requirement.** `⛔_direction_of_the_bound` applies to every number here: **a synthetic render is easier than a journal figure**, so each figure bounds real-figure reading error only **from below**.
- **No universal journal requirement and no lower bound for real figures may be drawn from synthetic ease.** A general reporting requirement remains **UNKNOWN**. The most that is supportable inside stated limits: *across four synthetic 59-patient cohorts differing in where the censoring sits, extending the printed risk table's time extent improved censored recovery in all four, whereas increasing its row count changed the read arm's censored recovery in a direction that depended on both cohort shape and line width.* That is a statement about this instrument on these cohorts, not a rule for journals.
- **Nothing here creates a publication, a manuscript admission or a clinical-result admission.**

## Validation evidence

**RUN** (all in `/home/user/Rare-cancers`, Python 3, no network, no paid API, no GPU):

```
sha256sum research/modalities/km_digitize.py research/modalities/emc_ipd_survival.py \
          research/autonomy/.../S4-executed-artifacts/sweep.py
  -> 05aeeb4b… / a82420f0… / 28aa8e7c…   (all three MATCH the contract pins)

python3 -c "import PIL"
  -> ModuleNotFoundError: No module named 'PIL'          [dependency named, branch stopped]

time python3 sweep5.py > results.json 2> stderr.txt
  real 0m0.864s   user 0m0.847s   sys 0m0.016s
  EXIT=0                                                  [stderr.txt = 0 bytes]
  meta.total_seconds = 0.827
  MAX_KM_DEVIATION_as_imported = 0.05
  REQUIRE_RISK_TABLE_as_imported = true
  n_cohorts 4 / n_cells 40 / n_reconstructions 200
  determinism_selfcheck: 4 of 4 cohorts identical on re-derivation

python3 summarize5.py > SUMMARY-TABLES.txt   EXIT=0
sha256sum -c SHA256SUMS.txt                  -> 7 of 7 OK  (verification printed above)
df -h /  -> 20G avail at start AND end       (floor 10 GiB honoured)
```

Cross-checks against S4's retained originals (independent reproduction, not a re-run of S4's file): cohort hash `7deb0b9f61a765f8…` and clean `digitized_sha256` `48af484b67124d15…` both reproduce S4's recorded values byte-for-byte, and the anchor's exact arm at rows 8 / extent 0.933 again gives `events_delta 0`, `censored_delta −7`, `maxdev 0.0009` — the committed `exact_coordinates_baseline`.

**PROPOSED (NOT RUN):** any JPEG/compression scenario (`km_digitize.jpeg_roundtrip`, PIL absent); any non-uniform risk-row placement; any cohort size other than 59.

## Limitations

- Four cohorts, all n = 59, all synthetic, one renderer, one reader family, uniform row placement only. Shapes were chosen by me to be structurally distinct; they are not a sample of anything and nothing here estimates how often a shape occurs.
- Two of my three read variations (gridlines, lenient matcher) turned out to be **inert** — they change no pixel the matcher sees — so the rendering axis was effectively tested by `line_width_4` alone. That single scenario carries the whole "rendering reorders the ranking" observation and should be treated accordingly.
- Row spacing is not independently controllable at fixed extent or fixed density; that confound is inherited from S4's design and is not resolved here.
- The thick-line mechanism (more digitized points → better time resolution for the recursion) is a **hypothesis consistent with the observable point counts**, not a measured cause.
- `low_event` has no truth median (not reached), so all its median deltas are `None` by construction — that is a defined absence, not a missing measurement.
- The JPEG/compression branch is **UNKNOWN**, not absent: PIL is not installed and nothing was installed.
- Transfer limit: none of this constrains real journal figures except **from below**.

## Stop condition

Set: raw per-cell output durably written and verified, or a named missing capability with that branch stopped. **MET.** All 40 cells × 5 arms are in `results.json`, written to `/tmp/claude-0/s5-retained/` and verified by `sha256sum -c` (7 of 7 OK) before any cleanup; nothing was deleted. The one missing capability (Pillow / `km_digitize.jpeg_roundtrip` at `km_digitize.py:1495-1501`) is named and its branch stopped. The 20-minute experiment bound was not approached (0.864 s wall clock); disk floor honoured at both ends.

## Tool-call and wall-clock count actually used

**12 tool calls.** Wall clock 06:19:12Z → 06:22:24Z = **3 min 12 s**; executed experiment itself **0.864 s**. Well inside the ~40-call and 20-minute bounds; I stopped at acceptance rather than padding.

## Next concrete action

**One successor, and it follows directly from the strongest measured result rather than from an untested hunch:** the density effect was largely abolished by `line_width_4`, whose only observable difference is that the read curve carried roughly twice as many digitized points. The open question is whether **read-curve point count**, not row count, is what actually drives censored-count loss — testable by holding the cohort and risk table fixed and varying `render_km`'s `width` (figure pixel width, which changes time resolution without changing line rendering) across a few fixed values, then plotting censored recovery against the resulting point count. That is deterministic, Pillow-free, and again a set of **fixed prespecified scenarios**, not draws. It should be run on at least `emc_anchor` and `low_event`, since those are where the thick-line effect was largest, and it must not be described as a distribution.

I did **not** write any manuscript, shared-graph, registry or other repository file, ran **no** git operation, ran **no** network/paid/GPU work, and touched **no** held or closed route.

---

## ⛔ COLLECTOR DISPOSITION APPENDED 2026-09-08 — one transfer claim in the report above is CORRECTED

**The report above is preserved verbatim and is not rewritten.** This appendix corrects one sentence in it.

Its Limitations section ends: *"Transfer limit: none of this constrains real journal figures except **from
below**."* ⛔ **That is not established, and it conflicts with the binding contract.** Synthetic ease supports
**no** bound on real-figure error in either direction — not an upper bound, and **not a lower bound either**.
A synthetic render being easier than a journal figure is a statement about the *inputs*, not a proven ordering
of *reconstruction error* on real figures; deriving a floor for real figures from it is exactly the inference
the contract forbids.

**The corrected transfer statement:** these results constrain **only** the measured synthetic scenarios.
**No universal or general bound on real-figure reconstruction error is established here, in any direction.**
Everything reported is **sensitivity across fixed prespecified scenarios** — not random replication, not a
distribution, and not an inference beyond the cells actually measured. The same correction applies wherever
`⛔_direction_of_the_bound` is quoted in this campaign's synthetic work: it describes the committed artifact's
own caveat about its inputs, and it is not a licence to state a real-figure floor.

Every measured number, failure, null and hash in the report above stands unchanged. Only this transfer
inference is withdrawn.
