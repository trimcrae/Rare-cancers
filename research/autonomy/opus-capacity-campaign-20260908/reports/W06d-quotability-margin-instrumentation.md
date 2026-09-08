> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report below.

---

## Worker

- **Worker ID:** W06d — Lane 6 refill, successor to W06c.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt. I did not observe the served model. **No environment variable in this container names a model** — the `env` grep below returns no model identifier, so the self-report has no environmental corroboration. The coordinator should extract the actual runtime model from the child transcript.
- `date -u` at start: `Tue Sep  8 02:25:38 UTC 2026`; at end: `Tue Sep  8 02:27:08 UTC 2026`.
- **HEAD actually read: `b9a0257e6acff53ad22535cf2adf261313e0b250`.** Note this differs from the frozen read commit named in COMMON-BRIEF.md §1 (`92abbcb905cacf07f14b238db50d1b98f6590374`); I read the checkout as it stands. The three files I used (`emc_mortality_decomposition.py`, `emc-mortality-decomposition-inputs.json`, `emc-mortality-decomposition.json`, plus `research/data/emc-clinical-registry.json`) are all clean at this HEAD — `git status --porcelain research/` shows nothing outside the campaign report directory.
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

What is the smallest change to `research/manuscripts/emc_mortality_decomposition.py` that makes the file's own quotability rule — *"A horizon where most pairings are impossible should not be quoted at all"* — machine-enforced rather than left to a reader's arithmetic, and does it change any existing published number?

It is open because the rule currently exists only as English prose inside the `excluded_pairings.how_to_read_them` string of the generated artifact. Nothing computes the horizon's position against it, and W06c established that `cross_series["5_year"]` sits at exactly the boundary (6 impossible of 12) while the file publishes that horizon's median (58.6%) and range with no margin and no note.

**Stated plainly, once:** W06c's tipping point (π = 0.130 on the disease-specific side) is a **conditional sensitivity result** — the value of a swept hypothetical contamination parameter at which the 5-year band's smallest coherent pairing would flip to impossible. It is **not** a claim that `masunaga2025`, `japan2003`, `meisKindblom1999`, `drilon2008`, or any other named cohort contains misclassified tumours. No π value, contamination rate or sensitivity figure appears anywhere in the patch or the candidate artifact.

## Prior-work check

```
$ cd /home/user/Rare-cancers && rg -n -i "quotable_by_own_rule|impossible_fraction" --glob '!.git' | head -20
research/autonomy/opus-capacity-campaign-20260908/reports/W06c-cross-series-tipping-point.md:266: [W06c's "Next concrete action" naming exactly this successor]
```
The only hit is W06c's own successor nomination. Neither field name exists in the generator, the artifact, the tests, or anywhere else in the corpus — this is not a replay.

```
$ git ls-files | rg -i "mortality.decomposition"
research/manuscripts/emc-mortality-decomposition-inputs.json
research/manuscripts/emc-mortality-decomposition.json
research/manuscripts/emc_mortality_decomposition.py
research/manuscripts/tests/test_emc_mortality_decomposition.py
```
Four files; I read all four in full.

`CLOSED-WORK.md` read in full. Confirmed not replayed: PUB-EMC-CLASSIFICATION / the user-rejected registry ICD-O classification paper (this is a generator readout, not EMC calibration, and produces no new classification analysis); Brenca (untouched); GSE4303/GSE28866 (untouched); every unrecovered source (no retrieval attempted, no network used); lane 11 source-index (untouched). W06b (pool sensitivity) and W06c (cross-series sweep) read; this is their named successor, not a re-run of either sweep.

## Method / inputs

Read-only on the tree. All execution under `/tmp/claude-0/w06d/`, which mirrors the four repository paths so the generator's `ROOT = Path(__file__).resolve().parents[2]` resolves to the sandbox, never to `/home/user/Rare-cancers`.

Inputs (copied verbatim from HEAD `b9a0257`):
- `/home/user/Rare-cancers/research/manuscripts/emc_mortality_decomposition.py` (512 lines)
- `/home/user/Rare-cancers/research/manuscripts/emc-mortality-decomposition-inputs.json`
- `/home/user/Rare-cancers/research/data/emc-clinical-registry.json`
- `/home/user/Rare-cancers/research/manuscripts/emc-mortality-decomposition.json` (committed artifact, kept aside as `committed.json`)
- `/home/user/Rare-cancers/research/manuscripts/tests/test_emc_mortality_decomposition.py`

Tool: `python3` 3.11.15, no third-party packages (`pytest` is **not installed** in this container — see Validation evidence for the substitute runner). No network.

## Result

**1. Regeneration fidelity: byte-for-byte.** `PRIMARY` — Running the unmodified committed generator against the committed inputs and registry reproduces `emc-mortality-decomposition.json` **byte-identically**: `cmp` exit 0, md5 `19ef9f55b2ff4c1f6eb2dab62f8b2526` on both. There is no discrepancy to report, so I proceeded.

**2. The smallest change.** One module-level constant, one seven-line pure function, two assignments and two dict entries — 21 added lines in the generator, zero deletions, zero modifications. The rule is encoded once as `IMPOSSIBLE_FRACTION_QUOTABLE_MAX = 0.5` with the semantics that *most* means **strictly more than half**, so a horizon at exactly half passes with zero margin. The fraction is emitted **beside** the boolean rather than the boolean alone, precisely so the zero margin at 5-year is visible rather than hidden behind a `true`.

**3. Effect on published numbers: none.** `PRIMARY` — the JSON diff is four inserted lines and nothing else; `grep -c '^-[^-]'` over the diff returns **0** removed lines. A field-for-field check proves the candidate equals the committed artifact exactly once the two new keys are removed from each horizon, with the order of all existing keys unchanged.

**4. New field values** (`PRIMARY`, arithmetic on the committed artifact's own pairing counts):

| horizon | pairings_impossible / pairings_total | `impossible_fraction` | `quotable_by_own_rule` | margin to the rule |
|---|---|---|---|---|
| `5_year` | 6 / 12 | **0.5** | **true** | **zero** — one more impossible pairing (7/12) flips it to `false` |
| `10_year` | 2 / 6 | **0.3333** | **true** | one pairing of slack (3/6 still passes; 4/6 fails) |

Units: dimensionless fraction of enumerated cross-series pairings. n = 12 and 6 pairings respectively; these are exhaustive enumerations, not samples, so there is no sampling uncertainty on the fraction — the uncertainty lives in the underlying published survival percentages, not here.

Boundary behaviour of the helper, exercised directly (`PRIMARY`): `(0,12)→(0.0,True)`, `(6,12)→(0.5,True)`, `(7,12)→(0.5833,False)`, `(2,6)→(0.3333,True)`, `(3,6)→(0.5,True)`, `(4,6)→(0.6667,False)`, `(0,0)→(None,False)`.

**5. What this does and does not enforce.** The patch makes the rule *computed and emitted*, which is what turns it into something a downstream guard or reader can check without doing arithmetic. It does **not** suppress the 5-year median or range — suppression would change a published number and would be a policy decision for the generator's owner, not a readout. It touches no exclusion predicate: `coherent`, `impossible` and `undefined` are unchanged in definition, name and order.

### Routed patch (NOT APPLIED — I am read-only)

`research/manuscripts/emc_mortality_decomposition.py`:

```diff
--- a/research/manuscripts/emc_mortality_decomposition.py
+++ b/research/manuscripts/emc_mortality_decomposition.py
@@ -218,6 +218,23 @@
     return out
 
 
+# The file's own quotability rule, made machine-checkable rather than left to a reader's
+# arithmetic: "A horizon where most pairings are impossible should not be quoted at all."
+# MOST means strictly more than half, so a horizon sitting at EXACTLY half is quotable with
+# zero margin -- which is why the fraction is emitted beside the verdict instead of the
+# verdict alone. This is a READOUT of the existing coherent/impossible/undefined split; it
+# changes no exclusion predicate and suppresses nothing.
+IMPOSSIBLE_FRACTION_QUOTABLE_MAX = 0.5
+
+
+def quotability(n_impossible: int, n_total: int) -> tuple[float | None, bool]:
+    """(impossible fraction, does this horizon pass the file's own rule)."""
+    if n_total == 0:
+        return None, False
+    frac = n_impossible / n_total
+    return round(frac, 4), frac <= IMPOSSIBLE_FRACTION_QUOTABLE_MAX
+
+
 def cross_series(spec: dict) -> dict:
     """Pair every all-cause figure against every disease-specific figure, per horizon.
 
@@ -269,6 +286,8 @@
                 else:
                     coherent.append(d)
 
+        n_total = len(coherent) + len(impossible) + len(undefined)
+        imp_frac, quotable = quotability(len(impossible), n_total)
         shares = sorted(x["competing_share_of_deaths_pct"] for x in coherent)
         ceilings = sorted(x["antitumour_ceiling_pct_points"] for x in coherent)
         ac_vals = sorted(v for _, v in all_cause[h])
@@ -282,6 +301,8 @@
             "pairings_coherent": len(coherent),
             "pairings_impossible": len(impossible),
             "pairings_undefined": len(undefined),
+            "impossible_fraction": imp_frac,
+            "quotable_by_own_rule": quotable,
             "competing_share_of_deaths_pct_range": [shares[0], shares[-1]] if shares else None,
             "competing_share_of_deaths_pct_median": (
                 shares[len(shares) // 2] if shares else None
```

The regenerated `emc-mortality-decomposition.json` follows from re-running the generator; it must **not** be hand-edited (generated-output convention). Its complete diff is in Validation evidence.

## Validation evidence

Environment for every command: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `python3` 3.11.15, working directory `/tmp/claude-0/w06d/…`, no network used. Repository read at HEAD `b9a0257e6acff53ad22535cf2adf261313e0b250`.

**RUN — 1. Regeneration fidelity (unmodified generator, sandbox copy of committed inputs)**

```
$ cd /tmp/claude-0/w06d/repo && python3 research/manuscripts/emc_mortality_decomposition.py
wrote research/manuscripts/emc-mortality-decomposition.json
  DIRECT  Japanese national registry, localised surgical: 4/13 deaths were not EMC deaths = 30.8% (ceiling 6.7 pts)
  DIRECT  Japanese national registry, metastatic at diagnosis: 1/10 deaths were not EMC deaths = 10.0% (ceiling 31.0 pts)
  within  Meis-Kindblom 1999 pathology series: at 10y, 39.4% of deaths were not EMC deaths (antitumour ceiling 18.2 pts)
  cross   5_year: competing share [13.0, 70.0]% (median 58.6%), ceiling [8.7, 24.2] pts, 6/12 pairings coherent (6 impossible, 0 undefined)
  cross   10_year: competing share [50.0, 57.1]% (median 57.1%), ceiling [15.0, 15.0] pts, 4/6 pairings coherent (2 impossible, 0 undefined)
  background check: RUN
  BG localised: observed 3.0% vs background 3.1% -> ratio 0.97 (95% CI 0.38-2.41)
  BG metastatic: observed 3.4% vs background 3.3% -> ratio 1.04 (95% CI 0.18-5.18)
EXIT=0
$ cmp /tmp/claude-0/w06d/committed.json research/manuscripts/emc-mortality-decomposition.json
CMP_EXIT=0
$ md5sum committed.json research/manuscripts/emc-mortality-decomposition.json
19ef9f55b2ff4c1f6eb2dab62f8b2526  /tmp/claude-0/w06d/committed.json
19ef9f55b2ff4c1f6eb2dab62f8b2526  research/manuscripts/emc-mortality-decomposition.json
```

**RUN — 2. Patched generator, and the full JSON diff**

```
$ cd /tmp/claude-0/w06d/patched && python3 research/manuscripts/emc_mortality_decomposition.py
[stdout identical to the run above, line for line]
GEN_EXIT=0
$ diff -u /tmp/claude-0/w06d/committed.json research/manuscripts/emc-mortality-decomposition.json
--- /tmp/claude-0/w06d/committed.json	2026-09-08 02:25:56.399958443 +0000
+++ research/manuscripts/emc-mortality-decomposition.json	2026-09-08 02:26:36.712946444 +0000
@@ -87,6 +87,8 @@
    "pairings_coherent": 6,
    "pairings_impossible": 6,
    "pairings_undefined": 0,
+   "impossible_fraction": 0.5,
+   "quotable_by_own_rule": true,
    "competing_share_of_deaths_pct_range": [
     13.0,
     70.0
@@ -155,6 +157,8 @@
    "pairings_coherent": 4,
    "pairings_impossible": 2,
    "pairings_undefined": 0,
+   "impossible_fraction": 0.3333,
+   "quotable_by_own_rule": true,
    "competing_share_of_deaths_pct_range": [
     50.0,
     57.1
DIFF_EXIT=1   (diff's "files differ" status; the difference is the four insertions above and nothing else)
```

That is the diff **in full** — two hunks, four added lines, no removed or modified lines. The generator's own stdout summary line is unchanged in every character, including the `6/12` and `4/6` pairing counts.

**RUN — 3. Acceptance property, proved by execution**

```
$ diff -u committed.json patched/.../emc-mortality-decomposition.json | grep -c '^-[^-]'
0
$ python3  [strips exactly {impossible_fraction, quotable_by_own_rule} from each horizon and compares]
PROVED: candidate == committed field-for-field after removing exactly the 2 new keys per horizon; key order of existing keys unchanged
  5_year: impossible 6/12 -> impossible_fraction=0.5, quotable_by_own_rule=True
  10_year: impossible 2/6 -> impossible_fraction=0.3333, quotable_by_own_rule=True
PROOF_EXIT=0
```
The assertions in that script cover: both new keys present on every horizon; the stripped horizon dict equal **and** in identical key order to the committed one; and the whole document equal outside `cross_series`. Any failure would have raised.

**RUN — 4. Existing test suite against the patched generator — 19/19 pass**

```
$ python3 -m pytest research/manuscripts/tests/test_emc_mortality_decomposition.py -q
/usr/local/bin/python3: No module named pytest
PYTEST_EXIT=1
```
`pytest` is **not installed in this container**. This is an honest tooling gap, not a pass. Substitute: the test module uses no fixtures, marks or parametrisation, so I stubbed the `pytest` import and called every `test_*` function directly. That is a weaker runner than pytest (no assertion rewriting, no collection of module-level errors), and the result should be re-confirmed under the repository's real gate before merge.

```
$ python3 [stub runner over research/manuscripts/tests/test_emc_mortality_decomposition.py]
PASS test_a_genuine_zero_over_zero_is_undefined_rather_than_impossible
PASS test_a_no_death_cohort_paired_against_real_disease_deaths_is_impossible_not_undefined
PASS test_background_check_reports_not_run_rather_than_assuming_a_value
PASS test_background_check_runs_when_a_life_table_is_present
PASS test_cross_series_rows_are_not_returned_by_within_series
PASS test_decompose_splits_all_cause_mortality_into_disease_and_the_rest
PASS test_disease_mortality_above_all_cause_is_flagged_incoherent_not_returned_as_negative
PASS test_every_pairing_is_enumerated_not_just_the_extremes
PASS test_provenance_fails_when_a_quoted_registry_string_is_gone
PASS test_provenance_passes_when_the_string_is_still_there
PASS test_the_antitumour_ceiling_is_the_disease_mortality_there_is_to_remove
PASS test_the_committed_artifact_carries_no_negative_or_impossible_headline
PASS test_the_committed_artifact_states_its_directional_bias
PASS test_the_pooled_reference_joins_the_ten_year_disease_specific_band
PASS test_the_real_inputs_still_resolve_against_the_real_registry
PASS test_the_reported_band_excludes_impossible_pairings_and_counts_them
PASS test_within_series_pairs_the_horizon_nearest_the_actual_follow_up
PASS test_within_series_reports_its_own_estimator_mismatch
PASS test_zero_all_cause_mortality_gives_an_undefined_share_not_zero
19/19 passed, 0 failed
TESTS_EXIT=0
```
(Two of those — `test_the_committed_artifact_*` — read the artifact in the patched sandbox tree, i.e. the **candidate** JSON, so they also confirm the candidate satisfies the committed artifact's own guards.)

**RUN — 5. Tree untouched**

```
$ git status --porcelain research/ | grep -v opus-capacity-campaign
(no output)
$ git rev-parse HEAD
b9a0257e6acff53ad22535cf2adf261313e0b250
```
No repository file was written. All writes are under `/tmp/claude-0/w06d/`.

**PROPOSED (NOT RUN)** — the following are *not* part of the routed patch and I did not execute them:
- `scripts/preflight.sh` / the repository's real pytest gate on the patched generator. Blocked by the missing `pytest` and by the read-only constraint. The generator's owner must run it.
- A companion guard test asserting `quotable_by_own_rule` on the committed artifact. I deliberately did **not** author one: a guard that fails the build when a horizon becomes unquotable is a policy decision (it would change what the repository does when the 5-year horizon tips), and COMMON-BRIEF §2 forbids me authoring my own acceptance criteria. Nominated, not written.

## Limitations

- **Not applied.** I am read-only; the patch is routed to the generator's owner. Nothing here is merged, and the committed artifact at HEAD `b9a0257` still lacks both fields.
- **The 5-year zero margin is exposed, not fixed.** `quotable_by_own_rule: true` at `impossible_fraction: 0.5` is the honest reading of "most means more than half", but a reader who sees only the boolean learns nothing about the margin. That is why the fraction ships alongside it. Whether a horizon at exactly half *ought* to be quotable is a judgement the generator's owner must make; I did not make it, and changing the threshold to `< 0.5` would flip 5-year to `false` and would be a substantive editorial change rather than a readout.
- **Threshold semantics are a reading of prose.** The rule text says "most", which I read as strictly greater than half. That reading is stated in the patch comment so it can be disputed rather than assumed.
- **`pytest` unavailable**; the 19/19 result comes from a hand-rolled runner, which is weaker than the repository's real gate. Not a substitute for it.
- **This is arithmetic on published summary percentages across heterogeneous studies.** It bears on no patient, asserts no efficacy, safety, selectivity or clinical readiness, and is not a prognosis. The underlying decomposition's own directional bias (competing share is an UNDER-estimate) is unchanged by this patch.
- The brief's frozen read commit (`92abbcb…`) does not match this checkout's HEAD (`b9a0257…`). The four files I used are clean at the HEAD I read, but a coordinator applying this patch should confirm the generator has not moved between those commits.

## Stop condition

Set: regeneration fidelity established by execution; a drafted patch run to produce a candidate artifact; a full diff proving no existing value changes; the new fields' values reported for both horizons.

**Met, all four.** Fidelity is byte-for-byte (md5 match, `cmp` exit 0). The patch ran, exit 0. The diff is four inserted lines with zero removals, shown in full, and field-for-field equality after key removal was proved by an executed assertion script. The values are 5-year `0.5` / `true` and 10-year `0.3333` / `true`. Returning now.

## Tool-call and wall-clock count actually used

9 tool calls. Wall clock 02:25:38Z → 02:27:08Z = **1 minute 30 seconds**. Well inside the ~40-call / ~40-minute target.

## Next concrete action

**One successor, and it is a decision to be taken by a human or by the generator's owner, not another analysis.** With `impossible_fraction` emitted, the open question becomes: *should the 5-year horizon's median and range still be published at `impossible_fraction = 0.5`?* Three options exist — keep publishing with the fraction visible (this patch, no editorial change); tighten the rule to `< 0.5` so exactly-half stops being quotable (flips 5-year to `false` and demands a decision about the 58.6% median already in circulation); or add a guard test that fails the build when a horizon becomes unquotable. All three are policy, not arithmetic, and COMMON-BRIEF §2 bars me from authoring my own acceptance criteria — so lane 6 should route the decision rather than dispatch another worker at it. If the coordinator wants a lane-6 analytic successor instead, I see none that is genuinely open: the cross-series band has now been swept (W06c), its rule made machine-readable (here), and further sweeps would re-derive the same 12 pairings.
