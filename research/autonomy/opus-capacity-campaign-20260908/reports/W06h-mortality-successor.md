<!-- collected 2026-09-08T03:34:17Z by campaign coordinator; agent id ab86bb2454e326ce6; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ab86bb2454e326ce6.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W06h**, lane 6 refill, OPUS-CAPACITY-CAMPAIGN-20260908. Container `/home/user/Rare-cancers`.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as `claude-opus-5`. This is my own assertion; nothing I could run in this container verifies the served model. The coordinator must extract the actual per-child runtime model from the transcript.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:22:50 UTC 2026` | `Tue Sep  8 03:26:50 UTC 2026` |
| `git rev-parse HEAD` | `302c2b63f7cc3ff16e2690de46e90a644181635f` | `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f` |
| `git status --porcelain` | *(empty)* | *(empty)* |

**HEAD moved under me and I verified rather than assumed.** `git diff --stat 302c2b63..ff6bb01` = 7 files, 2013 insertions, 5 deletions — all of them campaign reports under `research/autonomy/opus-capacity-campaign-20260908/reports/` (W06g filled in, plus W13g, W21d, W26, W27, W29, W30). `git diff --name-only 302c2b63 HEAD --` restricted to the ten files this work used (both generators, the inputs JSON, both output artifacts, the clinical registry, the life-table probe, the paper, `IDEAS.md`, the L2 view) returned **nothing**: none of my inputs changed across the move.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — full literal output at start:

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
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy/truststore flags, no model identity)
NO_PROXY=... (as no_proxy above)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=... (as no_proxy above)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**No variable in this environment names a model.** The same grep at end returned the same set (spot-checked on `CLAUDE_CODE_VERSION=2.1.42`, `AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_EFFORT=medium`, `ANTHROPIC_BASE_URL=https://api.anthropic.com`, both tokens still redacted).

Write isolation held: `git status --porcelain` empty at both ends, no git write operation was run, `scripts/preflight.sh` was not run, and every generator invocation was made inside `/tmp/claude-0/w06h/`. Post-run sha256 of the four live artifacts that the generators would have overwritten:

```
fe47c13b575c0dc0ebf1f0013c28cbc86045eff2673b87f86d5a18443107df6b  research/manuscripts/emc-mortality-decomposition.json
5eddacdc662980b74e58198c224b02ede027c6bea7cec7f28b001586fae90668  research/manuscripts/emc-relative-survival.json
dff1c49c7459eb323355e3a55967d6fd4d93b61279aa8554c29229ce0c45fea1  research/literature/emc-host-factor-probe.json
f0739ae091959aa5a840531533c689a423e419c4790fb44140a5769157ece6ac  research/manuscripts/emc-mortality-decomposition-inputs.json
```

No network was used. No content-policy refusal occurred.

---

## Question

W06g checked the tree's INDEPENDENCE claims — that the relative-survival artifact and the direct cause split are independent — found no shared numeric input, and recorded that as *"checked and not contradicted"*, which it correctly called weaker than verified.

**The question I pursued:** trace every input of `research/manuscripts/emc_relative_survival.py` and `research/manuscripts/emc_mortality_decomposition.py` to its committed source; determine whether the two artifacts share any numeric input, any upstream artifact, any life table, or any published survival figure, directly or transitively through an inputs cache; and settle it **by perturbation with real exit codes** rather than by reading. Then say which of the tree's independence sentences survive.

**Second question, from W06g's flagged observation:** the whole-cohort 10-year background check (ratio 1.77) and the per-stratum horizon-matched checks (ratios 0.97, 1.04) are presented side by side as two closed checks. Establish from the code whether both expected sides derive from the same WHO GHO life table, and say plainly whether they are two checks or two *independent* checks.

It is open because W06g's method — reading for a shared numeric input and finding none — cannot see a coupling that runs through a hand-copied cache, and cannot distinguish "no shared input" from "shared input, decoupled by a stale copy."

## Prior-work check

Commands run against the live checkout:

- `grep -n -i "independen\|share no input\|no shared" research/manuscripts/emc-mortality-mechanisms-paper.md research/IDEAS.md systems/views/L2-rt-competing-mortality.md research/manuscripts/emc-relative-survival.json` — located every independence sentence the dispatch named (line numbers below; they differ slightly from W06g's, and I quote current ones).
- `grep -rn "1\.77" --include=*.md --include=*.json research systems` — 10 hits; the load-bearing ones are `research/autonomy/research-ledger.json:316` and `:356` and `reports/W06e-margin-to-reversal-ranking.md:136,154,170`.
- `grep -rn "21\.7 per cent\|21\.7%"` across the paper and the L2 view; `grep -c "21\.7"` against both generated artifacts; `grep -rln "direct_cause_split_pooled"`.
- `sed -n` reads of both generators in full, the inputs JSON's `background_mortality` block, and the life-table probe.

Prior work I read and am **not** replaying:

- **W06g** (`reports/W06g-mortality-relabel-matrix.md`, now 64 lines at `ff6bb01`; it was 6 lines at my start commit and filled in during the HEAD move). Its own record states the primary report body is **lost to a transcript defect** and what stands is a **coordinator transcription, SECONDARY**. Its same-value collision matrix (75 scalars, 57 distinct, 15 shared values, 21 pairs, 701 generator runs), its three-plus-one re-labels, its `pairings_undefined` counterexample, and its 0.1-point rounding finding on `direct_cause_split[1]` are **not re-derived here** and are **not** re-reviewed. I extend exactly the one item it named as its successor.
- **W06e** (`reports/W06e-margin-to-reversal-ranking.md:136,154,170`) already established, as PRIMARY, that the 1.77 whole-cohort ratio's margin against the "far above 1" gate is **UNCOMPUTABLE because the threshold is prose with no number**, and that the paper answers that gate by quoting 0.97 and 1.04 and never 1.77. I do not re-open that; I answer a different question about the same pair — whether their *expected sides* are independent.
- **W06d** and **W06f** are quotability-margin and coherent-share instrumentation and do not bear on input tracing; I read their scope, not their bodies in full.
- `CLOSED-WORK.md`: I am not touching the **user-rejected registry ICD-O classification paper**, I introduce **no misclassification parameter**, and I did not attempt any denied source route.

Nothing here is a restatement: no prior artifact perturbs one generator's input and measures the other generator's output.

## Method and inputs

**Files traced (all at `ff6bb01`, none changed across the HEAD move):**

| Path | Role |
|---|---|
| `research/manuscripts/emc_relative_survival.py` | generator A |
| `research/manuscripts/emc_mortality_decomposition.py` | generator B |
| `research/manuscripts/emc-mortality-decomposition-inputs.json` | `INPUTS` — read by **both** |
| `research/literature/emc-host-factor-probe.json` | `LIFETABLE` — read by A |
| `research/data/emc-clinical-registry.json` | `REGISTRY` — read by B (provenance blob only) |
| `research/manuscripts/emc-mortality-decomposition.json` | B's output, and **`DECOMP`, an input of A** |
| `research/manuscripts/emc-relative-survival.json` | A's output |

**Sandbox.** `/tmp/claude-0/w06h/base/`, built with `tar --exclude=./.git` from the live tree, containing only the seven files above plus their directories. Verified layout:

```
$ python3 -c "import pathlib;print(pathlib.Path('/tmp/claude-0/w06h/base/research/manuscripts/emc_relative_survival.py').resolve().parents[2])"
parents[2]= /tmp/claude-0/w06h/base
```

A generator's `ROOT = Path(__file__).resolve().parents[2]` therefore resolves inside the sandbox and cannot reach `/home/user/Rare-cancers`. **Every** invocation of either generator in this report was made with `cwd` inside `/tmp/claude-0/w06h/<experiment>/`; the live tree was never a `ROOT`.

An earlier, larger scratch copy of the whole tree filled the container filesystem (`ENOSPC`, 617 MB free of a 97 %-full `/dev/vda`) and destroyed two commands' output. I recorded that rather than working around it, deleted the copy, and rebuilt the 492 KB minimal sandbox. No result below comes from the lost runs.

**Perturbation design.** Copy `base` → experiment dir, mutate one JSON field, run B then A (that order, because A reads B's output), then diff every numeric leaf of both output artifacts against `base`'s. Exit codes captured per generator. Python 3.11.15.

## Result

### R1. Baseline fidelity — the sandbox reproduces the committed artifacts exactly

`PRIMARY.` Both generators run at exit 0 on the untouched sandbox and produce files byte-identical to what is committed:

```
EXIT_DECOMP=0
EXIT_REL=0
IDENTICAL research/manuscripts/emc-mortality-decomposition.json
IDENTICAL research/manuscripts/emc-relative-survival.json
```

Every diff below is therefore attributable to the single field I changed.

### R2. Full input trace — three shared couplings, found by reading and confirmed by execution

`PRIMARY.`

| Coupling | Kind | Direction |
|---|---|---|
| `emc-mortality-decomposition-inputs.json` | **shared input file** | read by both generators |
| `series[].overall_survival` inside that file | **shared numeric input** | drives A's relative survival *and* B's `within_series` + `cross_series` |
| `emc-mortality-decomposition.json` | **shared upstream artifact** | B's **output** is A's **input**; A republishes B's cause-split values |
| WHO GHO life table `emc-host-factor-probe.json` | **shared life table, via a hand-copied cache** | read directly by A; reaches B as two numbers transcribed into the inputs file |

The cache is explicit in the inputs file: `"life_table_artifact": "research/literature/emc-host-factor-probe.json"`, `"blended_annual_rate_55_59": 0.009856`, `"ten_year_background_mortality": 0.1133`. I re-derived **both** cached numbers from the four `nMx` values in the probe artifact using the formulas the artifacts themselves document:

```
DERIVED from life table: (0.009856, 0.1133)   CACHED in inputs: 0.009856 0.1133
```

Exact match to the stored precision, both quantities. `blended_annual_rate_55_59` = 0.66 × 0.011437434 + 0.34 × 0.006786214; `ten_year_background_mortality` = 1 − [0.66·exp(−5(m♂55-59+m♂60-64)) + 0.34·exp(−5(m♀55-59+m♀60-64))]. These are **not** two life tables. They are two functions of one.

### R3. Perturbation matrix — seven experiments, all exit 0

`PRIMARY.` "Fields moved" = numeric/string leaves whose value changed against baseline.

| # | Perturbation | decomp exit | rel exit | fields moved in `emc-mortality-decomposition.json` | fields moved in `emc-relative-survival.json` |
|---|---|---|---|---|---|
| E1 | life-table `nMx` male 55-59 ×1.10, **file only** | 0 | 0 | **0** | **54** |
| E2 | the two cached derivatives ×1.10, **inputs file only** | 0 | 0 | **10** (all background checks) | **0** |
| E3 | life table ×1.10 **with its cache propagated consistently** | 0 | 0 | **10** | **54** |
| E4 | `other_cause_death.events` 4 → 8 (localised) | 0 | 0 | **5** (all `direct_cause_split[0]`) | **1** (the echoed cause-split value only) |
| E5 | one `overall_survival["10"]` − 0.05 | 0 | 0 | **7** (`within_series`, `cross_series`) | **6** (that series' RS row) |
| E6 | `cohort_sex_ratio_male` 0.66 → 0.50 | 0 | 0 | **0** | **59** |
| E7 | `cohort_age_median` 55 → 60 | 0 | 0 | **0** | **1** (`life_table.start_age` echo) |

**E3 is the refutation.** Treating the WHO GHO table as the single quantity it is — perturbing it at source and propagating its own documented derivation into the cache — moves **both** artifacts:

```
### e3_lifetable_with_cache   exit codes {'decomp': 0, 'rel': 0}
  DECOMP: 10 changed leaf fields
    .background_mortality_check.ratio_observed_to_expected: 1.77 -> 1.72
    .horizon_matched_background_check[0].ratio_observed_to_expected: 0.97 -> 0.9
    .horizon_matched_background_check[1].ratio_observed_to_expected: 1.04 -> 0.97
  RELSURV: 54 changed leaf fields
    .convergence.relative_survival_competing_share_pct_median: 23.0 -> 24.5
    .series[0].relative_survival: 0.9454 -> 0.9489
```

**E1 vs E2 shows why W06g's read-based check came back clean, and why the clean answer was not the true one.** Perturbing the life-table *file* alone moves only A (E1: decomp 0 fields); perturbing the *cached copy* alone moves only B (E2: relsurv 0 fields). Each half-test looks like independence. The coupling is real and is hidden by the hand-copied cache — which is a **provenance defect, not evidence of independence**. If the WHO GHO figures were ever refreshed in one place and not the other, the artifacts would silently disagree about their own background mortality with no check catching it: `emc_mortality_decomposition.py`'s `verify_provenance()` checks `registry_verbatim` strings against the clinical registry and checks **nothing** about the life-table numbers.

**E5 is a second, independent refutation, on the survival side.** `series[].overall_survival` in the shared inputs file feeds A's relative-survival estimator *and* B's `within_series`/`cross_series`. One edit moved six fields in A and seven in B. This is a shared **published survival figure**, exactly the category the dispatch asked about.

**E4 establishes the narrow negative cleanly.** Doubling a cause-split count moved five fields in B, all inside `direct_cause_split[0]`, and moved exactly **one** field in A — `.convergence.cause_split_competing_share_pct[0]: 30.8 -> 47.1`, the value A *copies out of B's artifact for display*. **No relative-survival estimate moved**: not one `relative_survival`, `excess_mortality_pct`, `competing_share_of_deaths_pct`, the pooled median, or the band. And in the reverse direction, across E1, E3, E5, E6 and E7, **`direct_cause_split` never moved a single field**. The clean zero the dispatch described exists — but only for this one narrow pair.

### R4. Verdict on each independence sentence

`PRIMARY.` Quoted verbatim at current `file:line`. W06g's line numbers were taken before the report commits landed; the sentences are the ones it named.

| # | Location | Sentence (verbatim, trimmed to the claim) | Verdict |
|---|---|---|---|
| 1 | `research/manuscripts/emc-mortality-mechanisms-paper.md:80` | "…against 21.7 per cent from the cause split; **the two methods share no input.**" | **REFUTED as written.** True of the two *estimators*' numeric ingredients (E4 both directions). False of "the two methods" as implemented: they share an inputs file, a published survival figure (E5), a life table (E3), and one reads the other's artifact. |
| 2 | `…paper.md:87` | "**Two independent methods** agree on the size of the competing fraction." | **SURVIVES, narrowly.** The relative-survival estimate and the direct cause split have disjoint numeric ingredients — verified, not merely unrefuted. "Independent" is doing estimator work here, not artifact work. |
| 3 | `…paper.md:162` | "…it is **independent of the cause-split** described above **and shares none of its inputs.**" | **First clause SURVIVES; second clause REFUTED.** "Independent of the cause-split" is verified by E4. "Shares none of its inputs" is false: `emc_relative_survival.py` line `DECOMP = ROOT / "research/manuscripts/emc-mortality-decomposition.json"` makes the cause-split artifact *literally an input file of the relative-survival generator*. |
| 4 | `…paper.md:253` | "### 3.5 **Agreement between two independent estimates**" | **SURVIVES.** Heading scopes the claim to *estimates*, which is the level at which it is true. |
| 5 | `…paper.md:256` | "**The two share no input**: one is published all-cause survival divided by a national life table, the other is counts of patients a registry assigned a cause to, and neither can be derived from the other." | **PARTLY REFUTED.** "Neither can be derived from the other" **survives** (E4, both directions). "The two share no input" is **false at the file level and misleading at the numeric level**: the relative-survival side's numerator *is* `series[].overall_survival` out of the same JSON that carries the cause-split counts, and its denominator is the same WHO GHO table the decomposition's background checks use. |
| 6 | `…paper.md:299-302` | "The relative survival analysis was performed because it does not need that assignment, and **its agreement with the cause split provides evidence that the assignment, where made, is not badly wrong.**" | **SURVIVES.** Makes no shared-input claim; rests only on the estimators' disjointness, which is verified. |
| 7 | `research/IDEAS.md:166` | "…a figure relative survival and registry cause attribution **agree on despite sharing no input**…" | **REFUTED as written**, same ground as #1 and #5. |
| 8 | `systems/views/L2-rt-competing-mortality.md:80` | "…a figure relative survival and registry cause attribution **agree on despite sharing no input**…" | **REFUTED as written.** (Generated view; `systems/views/` is generated, so the repair belongs upstream, not here.) |
| 9 | `research/manuscripts/emc-relative-survival.json:189` | "Relative survival and the cause-split are **INDEPENDENT**. One never touches a cause of death; the other is built entirely out of causes of death." | **SURVIVES.** Scoped to the two estimators and true of them. |
| 10 | `research/manuscripts/emc-relative-survival.json:210` | "**They share no input**: one is published all-cause survival divided by a national life table, the other is counts of patients a registry assigned a cause to. Neither can be derived from the other…" | **PARTLY REFUTED**, identically to #5 — and this is the sentence with the sharpest problem, because it is emitted *by the very script that opens the cause-split artifact to read it*. |

**Six of ten survive; four are refuted as written and two of those four are partly true.** The pattern is exact: every sentence scoped to *the two estimates* holds and is now verified rather than merely unrefuted. Every sentence that generalises to *inputs*, *methods* or *artifacts* is false.

### R5. The 1.77 question — two checks, not two independent checks

`PRIMARY, and the answer is plain.`

`research/autonomy/research-ledger.json:316` presents them as a pair: *"both the whole-cohort 10-year check (ratio 1.77) and the per-stratum horizon-matched check (ratios 0.97, 1.04) are run and folded into research/manuscripts/emc-mortality-decomposition.json"* (`:356` repeats it). The paper prints 0.97 and 1.04 at lines 80-81 and §3.6 (265-276) and never prints 1.77 — a point W06e already established.

From the code:

- `background_check()` (the 1.77) takes its expected side from `bg["ten_year_background_mortality"]` = **0.1133**.
- `horizon_matched_background()` (the 0.97 and 1.04) takes its expected side from `bg["blended_annual_rate_55_59"]` = **0.009856**, via `expected = 1 - exp(-rate * yrs)`.
- Both constants re-derive **exactly** from the same four `nMx` values in `research/literature/emc-host-factor-probe.json` (R2), same source, same country, same year (WHO GHO `LIFE_0000000029`, USA, 2021), same 0.66/0.34 sex blend. The 10-year figure uses bands 55-59 **and** 60-64; the horizon-matched figure uses band 55-59 only. Different horizons of one table.
- Confirmed by execution: **E2** perturbed only those two cached constants and moved **all three ratios at once** — 1.77→1.60, 0.97→0.88, 1.04→0.95.

**They are two checks. They are not two independent checks.** Their *observed* sides genuinely differ — the whole-cohort observed side is `median share × (100 − lowest all-cause survival)`, which W06g independently identified as a **re-label** rather than a second measurement, while the per-stratum observed sides are the integer counts 4/134 and 1/29. But their *expected* sides are one life table, and a life-table error would move all three ratios in the same direction simultaneously. Presenting them side by side as two closed checks invites a reader to treat the reassuring pair (0.97, 1.04) as corroborating against the same background the discordant one (1.77) was measured against. It does not corroborate; it is the same denominator asked at a different horizon.

I am **not** applying W06g's proposed disclosures and **not** editing the paper. This is a finding, not a repair.

### R6. Two incidental defects found while tracing

`PRIMARY.`

**(a) A dead field in the published relative-survival artifact.** `emc_relative_survival.py` reads `decomp.get("direct_cause_split_pooled")` to fill `convergence.cause_split_overall_competing_share_pct`. `emc_mortality_decomposition.py` never writes that key:

```
decomp top-level keys: ['_readme','generated_by','inputs','figures_home','directional_bias',
 'direct_cause_split','within_series','cross_series','background_mortality_check',
 'horizon_matched_background_check','reading_guide']
has direct_cause_split_pooled: False
relsurv cause_split_overall_competing_share_pct = None
```

So `cause_split_overall_competing_share_pct` is permanently `null` in the committed artifact. No published number is wrong; a field that exists to carry the headline comparator carries nothing.

**(b) The paper's headline comparator, 21.7 per cent, is produced by no generator.** `grep -c "21\.7"` returns **0** for both `emc-mortality-decomposition.json` and `emc-relative-survival.json`. It appears only in prose (`paper.md:79`, `:256`, `:391`; `L2-rt-competing-mortality.md:46`). It is arithmetically the pooled direct split across the two Masunaga strata: (4+1)/(13+10) = 5/23 = 21.7 %. That is an **enumeration over integer count fields**, so it is legal under POLICY §2.1 — no count is derived from a percentage, and I am not asserting the pooling is wrong. But it is a hand-carried number in the slot the dead field (a) was built to fill, and it therefore sits outside the generators' regeneration and provenance checks. This is a traceability gap, not a data error, and both halves have the same one-line fix.

## Validation evidence

### RUN

Environment for every command: container `container_0166QEHnXrRA8nCR59c9UG4k`, Linux 6.18.44, `Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]`, no network.

**Which copy each generator ran against — stated per run, as required.**

| Run | `cwd` (the generator's `ROOT`) | decomp exit | rel exit |
|---|---|---|---|
| baseline (large copy, superseded) | `/tmp/claude-0/w06h/base` (full-tree tar, later deleted for ENOSPC) | 0 | 0 |
| baseline (minimal, authoritative) | `/tmp/claude-0/w06h/base` | 0 | 0 |
| E1 | `/tmp/claude-0/w06h/e1_lifetable_file_only` | 0 | 0 |
| E2 | `/tmp/claude-0/w06h/e2_cached_derivatives_only` | 0 | 0 |
| E3 | `/tmp/claude-0/w06h/e3_lifetable_with_cache` | 0 | 0 |
| E4 | `/tmp/claude-0/w06h/e4_cause_count` | 0 | 0 |
| E5 | `/tmp/claude-0/w06h/e5_overall_survival` | 0 | 0 |
| E6 | `/tmp/claude-0/w06h/e6_sex_ratio` | 0 | 0 |
| E7 | `/tmp/claude-0/w06h/e7_age_median` | 0 | 0 |

**Neither generator was ever invoked against `/home/user/Rare-cancers`.** 16 generator invocations, all exit 0. `/tmp/claude-0/w06h/e1_lifetable_only/` is an empty directory left by the ENOSPC-killed first attempt; nothing was read from it.

Verbatim baseline output (minimal sandbox), decomposition:

```
wrote research/manuscripts/emc-mortality-decomposition.json
  DIRECT  Japanese national registry, localised surgical: 4/13 deaths were not EMC deaths = 30.8% (ceiling 6.7 pts)
  DIRECT  Japanese national registry, metastatic at diagnosis: 1/10 deaths were not EMC deaths = 10.0% (ceiling 31.0 pts)
  within  Meis-Kindblom 1999 pathology series: at 10y, 39.4% of deaths were not EMC deaths (antitumour ceiling 18.2 pts)
  cross   5_year: competing share [13.0, 70.0]% (median 58.6%), ceiling [8.7, 24.2] pts, 6/12 pairings coherent (6 impossible, 0 undefined)
  cross   10_year: competing share [50.0, 57.1]% (median 57.1%), ceiling [15.0, 15.0] pts, 4/6 pairings coherent (2 impossible, 0 undefined)
  background check: RUN
  BG localised: observed 3.0% vs background 3.1% -> ratio 0.97 (95% CI 0.38-2.41)
  BG metastatic: observed 3.4% vs background 3.3% -> ratio 1.04 (95% CI 0.18-5.18)
```

Verbatim baseline output, relative survival (tail):

```
  relative-survival competing share: 12.1-45.4%, median 23.0% over 8 series-horizons
  cause-split competing share:       [30.8, 10.0]%
```

Verbatim E4 diff (the narrow-independence result):

```
### e4_cause_count   exit codes {'decomp': 0, 'rel': 0}
  DECOMP: 5 changed leaf fields
    .direct_cause_split[0].all_cause_mortality_pct: 9.7 -> 12.7
    .direct_cause_split[0].competing_mortality_pct: 3.0 -> 6.0
    .direct_cause_split[0].competing_share_of_deaths_pct: 30.8 -> 47.1
    .direct_cause_split[0].other_cause_deaths: 4 -> 8
    .direct_cause_split[0].total_deaths: 13 -> 17
  RELSURV: 1 changed leaf fields
    .convergence.cause_split_competing_share_pct[0]: 30.8 -> 47.1
```

Verbatim E2 diff (the shared-life-table result):

```
### e2_cached_derivatives_only   exit codes {'decomp': 0, 'rel': 0}
  DECOMP: 10 changed leaf fields
    .background_mortality_check.expected_background_mortality_pct_at_10y: 11.3 -> 12.5
    .background_mortality_check.ratio_observed_to_expected: 1.77 -> 1.6
    .horizon_matched_background_check[0].expected_background_pct: 3.1 -> 3.4
    .horizon_matched_background_check[0].ratio_observed_to_expected: 0.97 -> 0.88
    .horizon_matched_background_check[1].expected_background_pct: 3.3 -> 3.6
    .horizon_matched_background_check[1].ratio_observed_to_expected: 1.04 -> 0.95
    (+ 4 CI bounds)
  RELSURV: 0 changed leaf fields
```

The harness (`/tmp/claude-0/w06h/harness.py`) copies `base`, applies one JSON mutation, runs `emc_mortality_decomposition.py` then `emc_relative_survival.py` via `subprocess.run(cwd=<experiment dir>)`, and reports every differing leaf via a recursive flattener. Perturbation magnitudes were chosen to be visible without leaving physically sensible ranges; the direction and magnitude of each moved value is arithmetic, not a finding about EMC.

### PROPOSED (NOT RUN)

- The one-line repair for R6: have `emc_mortality_decomposition.py` emit `direct_cause_split_pooled` as the enumerated integer pool (Σ`other_cause_deaths` / Σ`total_deaths` over `direct_cause_split`), which would populate the dead `cause_split_overall_competing_share_pct` field and put the paper's 21.7 % under generator provenance. **Not written, not run, and not authorised here** — I am read-only, and this touches a published artifact.
- A provenance assertion in `emc_mortality_decomposition.py` that re-derives `blended_annual_rate_55_59` and `ten_year_background_mortality` from `emc-host-factor-probe.json` and fails closed on drift, matching what `verify_provenance()` already does for `registry_verbatim`. **Not written, not run.**
- Any prose repair to the four refuted independence sentences. **Not attempted**, per dispatch.

## Limitations

- **This is a property of committed rows and code, and nothing else.** No death-decomposition or relative-survival readout here is a prognosis. Nothing here supports any claim about efficacy, safety, selectivity or clinical readiness. There is no wet lab.
- **Perturbed values are instrumentation, not measurements.** Every number in the E1-E7 "after" columns is an artifact of a deliberate edit to a sandbox copy. None of them is a reading of EMC and none may be quoted as one. The only measured quantities I report are the committed baseline values and the integer counts behind them.
- **I did not edit the clinical registry, any pooled proportion, or any interval**, and I introduced no misclassification parameter.
- **Independence is verified only against the perturbations I ran.** E1-E7 cover every field either generator reads that is numerically live: `series[].overall_survival`, `series[].disease_death`/`other_cause_death`, `background_mortality.{blended_annual_rate_55_59, ten_year_background_mortality, cohort_sex_ratio_male, cohort_age_median}`, and the life table's `nMx` values. I did **not** perturb `series[].disease_specific_survival`, `pooled_reference`, `median_followup_months`, `pairing`, or `registry_verbatim`; of these only the first two can move a published value, and both are read solely by generator B, so neither can create a coupling A does not already have through `overall_survival`. That reasoning is inference, not execution, and I flag it as such.
- **The verdicts in R4 are readings of what a sentence claims.** "Share no input" is unambiguous and is refuted. Whether "two independent methods" (#2) was *intended* to assert artifact independence or estimator independence is a question about authorial intent I cannot settle from the tree; I read it in the narrower sense under which it is true.
- **W06g's findings are SECONDARY to me.** Its primary report is lost to a transcript defect and what survives is a coordinator transcription. I did not re-derive its collision matrix, and where I cite it (the `observed_competing_mortality_pct_at_10y` re-label) I inherit its evidence class.
- **The ENOSPC event cost two commands' output.** No result in this report depends on them; the minimal sandbox was rebuilt and re-verified byte-identical against the committed artifacts before any experiment ran.
- **The container disk was at 97 % when I finished.** Later workers may hit the same wall.

## Stop condition

**Set up front:** return the moment all four hold — (1) every input of both generators traced to a committed source; (2) bidirectional perturbation executed with real exit codes, showing either a shared input that moves both or a clean zero; (3) each of the tree's independence sentences quoted at `file:line` with a survives/refuted verdict; (4) the 1.77-vs-0.97/1.04 question answered from the code as "two checks" or "two independent checks".

**MET, all four.** (1) done in R2. (2) done in R3 — seven experiments, 16 generator runs, all exit 0, yielding *both* outcomes: a clean zero for the narrow estimator pair and three shared couplings that move both artifacts. (3) done in R4 — ten sentences, six survive, four refuted as written. (4) done in R5 — **two checks, not two independent checks**, proven by exact re-derivation of both constants from one WHO GHO table and confirmed by E2 moving all three ratios together.

**W06g's "checked and not contradicted" is now settled, and it splits.** The narrow claim it could not verify is **verified**: relative survival and the direct cause split have disjoint numeric ingredients, and perturbing either moves nothing of the other's estimate. The broader claims the tree makes around it are **refuted**: the two artifacts share an inputs file, a published survival figure, a life table, and one reads the other.

## Tool-call and wall-clock count actually used

**30 tool calls** (2 `Read`, 28 `Bash`; 2 of the 28 returned no usable output because the temp filesystem filled). **4 minutes wall clock**, `03:22:50Z` → `03:26:50Z`. Both well inside the ~40/~40 target.

## Next concrete action

**One action, for the coordinator or the paper owner, not for me:** repair the four refuted independence sentences by narrowing them to the level at which they are true — replace "the two methods share no input" / "sharing no input" with a claim about the *estimates*, e.g. "the two estimates share no numeric ingredient: no figure entering one enters the other" — at `research/manuscripts/emc-mortality-mechanisms-paper.md:80`, `:162` (second clause only), `:256` (first clause only), and `research/IDEAS.md:166`. `systems/views/L2-rt-competing-mortality.md:80` is generated and must be fixed at its source and regenerated, never edited directly. The narrowed claim is now **verified by execution** (E4, both directions) rather than merely unrefuted, so this repair makes the paper's assertion stronger, not weaker. `research/manuscripts/emc-relative-survival.json:210` is generated by `emc_relative_survival.py` and needs the same narrowing in the script's `reading` string. This is a prose-scope correction with no effect on any published number, and it should carry the R5 sentence — that the whole-cohort and per-stratum background checks share their expected side and are two checks rather than two independent ones — since the same paragraph in `research-ledger.json:316` presents them as a corroborating pair.
