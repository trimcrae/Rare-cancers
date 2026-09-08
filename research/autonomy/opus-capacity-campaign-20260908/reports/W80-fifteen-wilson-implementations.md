<!-- collected 2026-09-08T05:03:52Z by campaign coordinator; agent id a1458c16d2e240348; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a1458c16d2e240348.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

W80, campaign OPUS-CAPACITY-CAMPAIGN-20260908, lane: cross-implementation numerical agreement of the repository's 15 `wilson()` definitions.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED — Claude Opus 5 (`claude-opus-5`).** The environment exposes no model variable; the literal output of the required command is below and contains no model identifier.

Start `date -u`: `Tue Sep  8 04:58:36 UTC 2026` · start `git rev-parse HEAD`: `d5034489077eee6a11ccee088bd5bfccf6f7a8e1` · start `git status --porcelain`: empty.
End `date -u`: `Tue Sep  8 05:01:04 UTC 2026` · end `git rev-parse HEAD`: `49ed4d4e94df6753a7300b893d718583f87a03e3` (coordinator commits during the run; campaign directory only) · end `git status --porcelain`: **empty — live tree untouched.**

```
env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'
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
(Three long proxy/no-proxy values are elided as `<same list as no_proxy>` / `<proxy/truststore flags>` for length; nothing model-identifying was removed.)

## Question

W60 measured that 15 files each define their own `wilson()`, that exactly one is guarded by the repository's one closed-form control (`research/modalities/tests/test_locoregional_eligibility.py:89`) and a second is bound to it by an identity assertion (`research/modalities/tests/test_emc_surgical_quality.py:157`), leaving thirteen unexercised by that control. **Do the fifteen agree?** Open because the thirteen have never been compared to each other or to a closed form by any executed test; W60 counted the definitions but did not call them.

## Prior-work check

- `grep -rn "def wilson" --include=*.py .` (excluding `.git`) → exactly 15 hits, matching W60's list. One of them is named `wilson95`, not `wilson` (`research/modalities/nr4a_paralogue_dynamics.py:136`) — W60's count is right, the shared name is not.
- Read in full: `research/autonomy/opus-capacity-campaign-20260908/COMMON-BRIEF.md` (641 lines), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, and `systems/POLICY-evidence.md` §2.2.
- Taken as given, not re-measured: W60's 15-file census and its opt-in-tier mutation results; W53's finding that `research/meta/meta-analysis.mjs` contains no Wilson at all; W48's enforcement census. §2.2 (quoted): "**95% confidence interval**: the **Wilson score interval** on (Σevents, Σdenom)… unlike the normal approximation."
- Nothing in `CLOSED-WORK.md` covers Wilson-implementation agreement. W25 not read or referenced.

## Method and inputs

1. **Source read first.** All 15 module tails inspected: **every one of the 15 guards its entry point with `if __name__ == "__main__":`** — none runs `main()` at import. (The in-source comments in `emc_endpoint_alternatives.py:609` and `orr_dcr_reread.py:55` claiming "importing … executes a full build at import time" are, at this HEAD, describing a hazard that the guards prevent. Module-level *data* construction still happens; measured import output was 0 bytes for all 15.)
2. **`cp -a` scratch copy** at `/tmp/claude-0/w80/repo` (985 MB incl. `.git`); every import ran with cwd inside the copy and `PYTHONDONTWRITEBYTECODE=1`. Nothing was executed against the live tree.
3. Harness `/tmp/claude-0/w80/harness.py` loaded each file by path with `importlib.util.spec_from_file_location`, stdout/stderr redirected, and called the function on a common battery of **18 inputs**: the control's three closed-form pairs `(0,10) (10,10) (1,2)`; boundaries `(0,1) (1,1) (0,0)`; small n `(1,3) (3,7) (4,5) (4,20)`; mid `(1,100) (28,100) (50,100) (99,100) (38,211)`; large n `(0,1000) (5,1000) (1000,1000)`.
4. Reference: closed-form Wilson score, `((p + z²/2n) ± z√(p(1−p)/n + z²/4n²)) / (1 + z²/n)`, no continuity correction, evaluated at both `z = 1.959963984540054` and `z = 1.96`, clamped to [0,1].
5. Return shapes normalised: 2-tuple/2-list `(lo,hi)`; 3-tuple `(p,lo,hi)` (`emc_locoregional_eligibility`, `hormone_partner_map`); dict with `ci95_lo_percent`/`ci95_hi_percent` (`emc_fusion_partner_pooling`).
6. Python `/usr/local/bin/python3`. No network, no GPU, no paid API. `scripts/preflight.sh` not run; `atr_hrd_sarcoma_series.py` not invoked; no `--refresh`/`--fetch`.

## Result

**Headline: 15 of 15 agree. Zero arithmetic divergences.** Every one of the fifteen computes the *same* Wilson score interval, with no continuity correction, no normal approximation, and no different interval family. All observable differences are presentational — rounding granularity, z-constant precision, clamping, return shape, and `n=0` behaviour.

### Table 1 — agreement to each implementation's own declared precision (all rows PRIMARY, measured)

Max |deviation| in *proportion units* across all 18 battery inputs, against the closed form at each z.

| # | Module (`def` line) | z used | rounding | max dev vs z=exact | max dev vs z=1.96 | verdict |
|---|---|---|---|---|---|---|
| 1 | `research/modalities/paralogue_pocket_asymmetric_read.py:150` | 1.959963984540054 | 4 dp | 4.931e-05 | 4.887e-05 | AGREES (≤ ½ ULP of 1e-4) |
| 2 | `research/modalities/hla_coverage.py:83` | 1.96 | 4 dp | 4.931e-05 | 4.887e-05 | AGREES |
| 3 | `research/modalities/aso_parent_null.py:480` | 1.96 | 5 dp | 9.601e-06 | **4.955e-06** | AGREES (≤ ½ ULP of 1e-5 at its own z) |
| 4 | `research/modalities/nr4a_paralogue_dynamics.py:136` (`wilson95`) | 1.959963985 | 4 dp | 4.931e-05 | 4.887e-05 | AGREES |
| 5 | `research/modalities/hormone_partner_map.py:297` | 1.959963984540054 | **none** | **1.110e-16** | 7.369e-06 | AGREES (machine roundoff) |
| 6 | `research/modalities/emc_locoregional_eligibility.py:137` | 1.959963984540054 | **none** | **0.000e+00** | 7.369e-06 | AGREES (bit-exact) — *the guarded one* |
| 7 | `research/modalities/nr4a3_tcip_reach.py:352` | 1.96 | 8 dp | 7.370e-06 | **4.874e-09** | AGREES (≤ ½ ULP of 1e-8 at its own z) |
| 8 | `research/manuscripts/emc_endpoint_alternatives.py:609` | 1.96 | 4 dp | 4.931e-05 | 4.887e-05 | AGREES |
| 9 | `research/manuscripts/emc_fusion_partner_pooling.py:86` | `Z95` = 1.959963984540054 (`:80`) | **1 dp of percent** = 1e-3 | 4.919e-04 | 4.903e-04 | AGREES (≤ ½ ULP of its 0.1-pp output) |
| 10 | `research/manuscripts/emc_systemic_therapy_pooling.py:821` | 1.96 | 4 dp | 4.931e-05 | 4.887e-05 | AGREES |
| 11 | `research/manuscripts/placebo_arm_calibration.py:89` | 1.96 | 4 dp | 4.931e-05 | 4.887e-05 | AGREES |
| 12 | `research/manuscripts/orr_dcr_reread.py:55` | 1.96 | 4 dp | 4.931e-05 | 4.887e-05 | AGREES |
| 13 | `research/manuscripts/emc_endpoint_discordance.py:79` | 1.96 | 4 dp | 4.931e-05 | 4.887e-05 | AGREES |
| 14 | `research/manuscripts/aso_reagent_coverage.py:84` | 1.96 | 4 dp | 4.931e-05 | 4.887e-05 | AGREES |
| 15 | `research/manuscripts/emc_mortality_decomposition.py:317` | 1.96 | **none** | 7.369e-06 | **0.000e+00** | AGREES (bit-exact at its own z) |

Rows 6 and 15 are bit-exact against the closed form at their own z; row 5 differs by 1.1e-16. Every other row's residual is entirely explained by its own `round()`.

**Cause of the two families of residual, from source:**
- **z constant.** Nine use the literal `1.96`; five use `1.959963984540054`; one uses the truncated `1.959963985`. **Maximum effect of z=1.96 vs the exact 97.5th normal quantile, measured across the battery: 7.369e-06 in proportion = 7.4e-04 percentage points.** Below the reporting precision of every artifact in the corpus, and invisible at 4 decimal places.
- **Rounding.** Granularities span 5 orders of magnitude: none (3 modules) / 1e-8 (1) / 1e-5 (1) / 1e-4 (9) / 1e-3 (1, as 0.1 pp).

**No implementation uses a continuity correction, a normal (Wald) approximation, Agresti–Coull, Jeffreys or Clopper–Pearson.** The only exact-interval code found nearby is `emc_endpoint_alternatives.binom_sf`, a separate function for a different purpose.

### Table 2 — behavioural (non-arithmetic) differences (PRIMARY, measured)

| Behaviour | Modules |
|---|---|
| `n=0` → `[None, None]` / `(None, None)` | 1, 2, 3, 8, 10, 11, 12, 13, 14 |
| `n=0` → `(None, None, None)` (3-tuple) | 5, 6 |
| `n=0` → `None` (scalar) | 4 |
| `n=0` → **`(0.0, 1.0)`** — a full-width interval, not a null | **15** `emc_mortality_decomposition:317` |
| `n=0` → **raises `ValueError`** | **9** `emc_fusion_partner_pooling:86` |
| clamps bounds to [0,1] | 3, 4, 5, 6, 9, 11, 12, 14, 15 |
| does **not** clamp | 1, 2, 7, 8, 10, 13 |
| returns `p` alongside the bounds (3-tuple) | 5, 6 |
| returns a dict of percents + `"interval": "Wilson score, 95%"` | 9 |

Measured across all 18 inputs: **no implementation ever produced `lo < 0`, `hi > 1`, or `lo > hi`.** Non-clamping is therefore latent, not live, on this battery — Wilson bounds are analytically in [0,1]. One cosmetic artefact of non-clamping is live: `nr4a3_tcip_reach.wilson(0, 10)` returns `[-0.0, 0.27754017]` and serialises to JSON as **`-0.0`** (verified: `json.dumps` → `[-0.0, 0.27754017]`).

### Table 3 — the closed-form control applied verbatim to all 15 (PRIMARY)

Control values from `test_locoregional_eligibility.py:85-87`: `(0,10)→(0.0, 0.2775)`, `(10,10)→(0.7225, 1.0)`, `(1,2)→(0.0945, 0.9055)`, at the control's own `pytest.approx(abs=1e-4)`.

- **14 of 15 PASS** on values.
- **1 FAILS: `emc_fusion_partner_pooling` only** — `0.278 / 0.722 / 0.095 / 0.905` vs the control's 4-decimal targets, max deviation **4.69e-04**. This is **not an arithmetic disagreement**: it computes with the exact `Z95` constant and then rounds its *published output* to 0.1 percentage points, which is coarser than the control's 1e-4 tolerance. Its unrounded arithmetic is the same formula as row 6's bit-exact one.
- Separately, the control's call form `_, got_lo, got_hi = loco.wilson(ev, dn)` only unpacks the **3-tuple** shape, so as written it is applicable verbatim to rows 5 and 6 alone; the other thirteen require shape normalisation before the same assertion can be made. This is a fact about the control's coupling, not about the arithmetic.

### Which committed artifact each implementation's intervals reach (SECONDARY — read from each module's `OUT` constant, not by regenerating)

| Module | Published artifact |
|---|---|
| 1 | `research/modalities/paralogue-pocket-asymmetric-read.json` |
| 2 | `research/modalities/hla-coverage.json` |
| 3 | `research/modalities/aso-parent-null.json` |
| 4 | `research/modalities/nr4a-paralogue-dynamics.json` |
| 5 | `research/modalities/hormone-partner-lane.json` |
| 6 | `research/modalities/emc-locoregional-eligibility.json` (also consumed by `emc_surgical_quality` via the `sq.wilson is loco.wilson` identity assertion) |
| 7 | `research/modalities/nr4a3-tcip-reach.json` |
| 8 | `research/manuscripts/endpoint/emc-endpoint-alternatives.json` |
| 9 | `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` |
| 10 | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` |
| 11 | `research/manuscripts/endpoint/placebo-arm-calibration.json` |
| 12 | `research/manuscripts/endpoint/orr-dcr-reread.json` |
| 13 | `research/manuscripts/endpoint/emc-endpoint-discordance.json` |
| 14 | `research/manuscripts/aso/fusion-junction-aso-reagent-coverage.json` |
| 15 | `research/manuscripts/emc-mortality-decomposition.json` |

**Because there are no arithmetic divergences, no committed artifact's published intervals are affected by a divergence.** The largest quantity any published interval could move if every module were switched to the exact z and full precision is **7.4e-04 percentage points**, which does not change a single figure at any rounding used in the corpus.

## Validation evidence

All RUN. Environment: `/home/user/Rare-cancers` at start HEAD `d5034489`, end HEAD `49ed4d4e`; `PYTHONDONTWRITEBYTECODE=1`; cwd for every import `/tmp/claude-0/w80/repo`.

```
$ grep -rn "def wilson" --include=*.py . | grep -v '\.git'      # 15 hits, exit 0
$ mkdir -p /tmp/claude-0/w80 && cp -a /home/user/Rare-cancers /tmp/claude-0/w80/repo   # exit 0, 985M
$ cd /tmp/claude-0/w80/repo && PYTHONDONTWRITEBYTECODE=1 python3 /tmp/claude-0/w80/harness.py
done 15 of 15
EXIT=0
```
Import side-effects, verbatim: `ok=True out=0` for all fifteen modules (`out` = bytes written to stdout+stderr during `exec_module`). Zero import-time output, zero import failures, zero writes.

Out-of-range check, verbatim: `out-of-range or inverted bounds: []`.

Negative-zero check, verbatim: `[-0.0, 0.27754017] [-0.0, 0.27754017]` (repr, then `json.dumps`).

Write-isolation proof, verbatim:
```
$ git rev-parse HEAD
49ed4d4e94df6753a7300b893d718583f87a03e3
$ git status --porcelain
(empty)
$ rm -rf /tmp/claude-0/w80   # scratch deleted, confirmed absent from /tmp/claude-0 listing
```

No content-policy refusal occurred. PROPOSED (NOT RUN): nothing — I authored no test, patch, gate or repair, per instruction. `pytest` was not run on the two control tests; I applied their literal assertion values in the harness instead, which is a replication of the control's arithmetic, not a run of the control.

## Limitations

- Agreement is measured on **18 inputs**, not proved for all (k,n). It is a battery, not a proof; the boundaries and the control's own values are included, but e.g. non-integer `events` (the `events: 3.5` hazard W53 recorded elsewhere) was not exercised.
- The comparison is of the **functions**, not of the artifacts. I did not regenerate any artifact and did not verify that any committed JSON actually contains the value its module would now compute. A module could be stale against its own `wilson()` and this run would not see it.
- `emc_fusion_partner_pooling` was compared through its dict's `ci95_*_percent` fields, which are the only bounds it exposes; whether an unrounded internal value reaches anything else is unchecked.
- Rounding granularity is read from source `round()` calls, not measured exhaustively; the deviation figures are the measured quantity.
- **An interval's width is a statement about arithmetic.** Nothing here bears on EMC efficacy, safety, selectivity or clinical readiness, and no published interval is restated as a clinical finding. Agreement between implementations is not evidence that any published number is correct — only that fifteen call sites compute the same function.
- I did not consolidate, refactor or repair anything; which module should own a shared helper is a maintainer's decision and is untouched here.

## Stop condition

Set up front: *return as soon as all 15 functions have been called on the common battery and each is classified AGREES/DIVERGES with a quantified deviation and a source-identified cause.* **MET.** All 15 imported and called successfully; all 15 classified; deviations quantified; causes identified from source.

## Tool-call and wall-clock count actually used

**16 tool calls**, wall clock **04:58:36Z → 05:01:04Z ≈ 2.5 minutes** (both well inside the ~40/~40 target). Scratch directory deleted.

## Next concrete action

The open successor in this lane is **artifact-level, not function-level**: check whether the fifteen committed JSON artifacts in the table above actually *contain* the intervals their now-verified-agreeing `wilson()` would produce from the inputs those same artifacts record — i.e. run each module's `--check`/verify mode (read-only, on a `cp -a` copy) and count how many artifacts are stale against their own arithmetic. That is the question this run could not answer and the one where a real defect could still hide, since W30c's "no gate runs the pooler" and W68's "these figures are unpinned, unlinted and unregenerated" both point at artifacts nothing re-derives. Note for whoever takes it: `emc_fusion_partner_pooling`'s 0.1-pp output granularity means any such comparison needs a per-module tolerance, not one global tolerance.
