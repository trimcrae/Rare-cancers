<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:10:00Z UTC
     agent id ac0b3580bb24f73ca ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ac0b3580bb24f73ca.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report below.

---

## Worker

- **Worker ID:** W06f — Lane 6 refill, named successor to W06e, in OPUS-CAPACITY-CAMPAIGN-20260908.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt. I did not observe the served model, and **no environment variable in this container names a model** — the `env` grep below contains no model identifier, so the self-report has no environmental corroboration. The coordinator must extract the actual runtime model from the child transcript.
- `date -u` at **start**: `Tue Sep  8 02:58:52 UTC 2026`. At **end**: `Tue Sep  8 03:03:01 UTC 2026`.
- **HEAD moved twice under me.** Read at start: `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8`. Inputs were copied at `4ec9da1e4d335911a92157cf7a402e3990fe5cee`. At end: `a87275c14897230041fde97c9965c9646474df7a`. I verified this does not affect anything I used: `git diff --stat` across **both** moves, over all six files I read (the generator, its inputs, the committed artifact, the registry, the test module, the paper), returned **empty output, exit 0** — byte-identical throughout. What actually moved were other workers' campaign reports (W07e, W10f, W13f, W17h). All three commits also differ from the frozen read commit named in COMMON-BRIEF.md §1 (`92abbcb…`); I read the checkout as it stands and say so.
- `git status --porcelain` at start: **empty**. At end: **empty**. I wrote nothing into the tree.
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

## Stop condition (stated up front, per dispatch)

Return the moment all four hold: (i) `smallest_coherent_share_pct` is computed for both horizons **from the committed inputs by my own arithmetic**, not taken from the prompt, and any discrepancy against W06e's stated 13.0 / 50.0 is reported; (ii) the closed form is confirmed **by execution** — a perturbed committed input, the **unmodified** committed generator, real exit codes, and the generator's own stdout quoted, with the coherence verdict flipping where predicted; (iii) the patch exists, the **unpatched** control reproduces the committed artifact exactly, and the patched artifact is proved identical apart from the added field; (iv) the readout's limits are stated plainly.

**MET, all four.** Result below. It was met with one correction to the framing, reported in §3.

## Question

**What is the smallest readout that tells a reader how close each horizon of `research/manuscripts/emc-mortality-decomposition.json` is to its own quotability gate — and is that readout correct?**

Open because W06d routed but did not apply two fields in pairing units, and W06e then showed that pairing units understate the case (the 5-year margin is *zero* in pairings but *1.30 percentage points* in the units the input actually moves in) and named `smallest_coherent_share_pct` as the fix. Nobody had checked whether that field is (a) the value W06e says it is, (b) actually a margin against the gate, or (c) new information at all.

## Prior-work check

```
$ rg -n 'smallest_coherent_share' --glob '!.git'
research/autonomy/opus-capacity-campaign-20260908/reports/W06e-margin-to-reversal-ranking.md:266: [W06e's "Next concrete action", naming exactly this field]
```
One hit, and it is my own predecessor's nomination. The field name exists nowhere else in the corpus.

```
$ rg -c 'smallest_coherent_share_pct' research/manuscripts/emc_mortality_decomposition.py \
                                      research/manuscripts/emc-mortality-decomposition.json
exit=1   (no matches in either file)

$ git ls-files | rg -i 'mortality.decomposition'
research/manuscripts/emc-mortality-decomposition-inputs.json
research/manuscripts/emc-mortality-decomposition.json
research/manuscripts/emc_mortality_decomposition.py
research/manuscripts/tests/test_emc_mortality_decomposition.py
```

`COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `systems/POLICY-evidence.md` and the three predecessor reports read in full. **Confirmed not replayed: PUB-EMC-CLASSIFICATION / the user-rejected registry ICD-O classification paper — I ran no EMC calibration analysis, admitted no new calibration on unchanged inputs, and introduced no misclassification parameter of my own.** W06c's π appears in this report only as a *stated input* (§3); I did not re-derive it and I did not sweep it. Brenca, Hofvander, paired Davis, promoter transfer, GSE4303/GSE28866, every unrecovered source (no retrieval, **no network used at all**) and lane 11's source index: all untouched. **POLICY-evidence §2.1 respected — no count anywhere below is derived from a percentage;** every count I quote (12 pairings, 6 impossible, 6 / 4 coherent) is read from the artifact's own integer fields or produced by enumeration.

## Method / inputs

Read-only on the Git tree. All execution under `/tmp/claude-0/w06f/`, which mirrors the repository paths so the generator's `ROOT = Path(__file__).resolve().parents[2]` resolves inside the sandbox and can never reach `/home/user/Rare-cancers`. Three sibling trees: `base/` (unpatched control), `patched/`, `perturb/`.

Inputs, copied verbatim at `4ec9da1` and verified byte-identical at `ce743d6` and `a87275c`:
- `/home/user/Rare-cancers/research/manuscripts/emc_mortality_decomposition.py` (512 lines)
- `/home/user/Rare-cancers/research/manuscripts/emc-mortality-decomposition-inputs.json`
- `/home/user/Rare-cancers/research/manuscripts/emc-mortality-decomposition.json` (held aside as `committed.json`, md5 `19ef9f55b2ff4c1f6eb2dab62f8b2526`)
- `/home/user/Rare-cancers/research/data/emc-clinical-registry.json`
- `/home/user/Rare-cancers/research/manuscripts/tests/test_emc_mortality_decomposition.py`
- `/home/user/Rare-cancers/research/manuscripts/emc-mortality-mechanisms-paper.md` (read for the cross-series check only)

**Reused as a stated input, not re-derived** (per dispatch): W06c's closed form — *"a coherent pairing flips to impossible exactly when π exceeds its own competing share"* — and its 5-year model-C tipping point **π = 0.130**. I state them and test their consequence; I did not reconstruct W06c's sweep.

Tools: `python3` 3.11.15, stdlib only, Linux 6.18.44-fc-v24. No network.

## Result

### 1. The two values, derived from the committed inputs — no discrepancy

I re-enumerated all pairings directly from `emc-mortality-decomposition-inputs.json` with my own arithmetic (`m_all = 1−S_OS`, `m_dis = 1−S_DSS`, share `= (m_all−m_dis)/m_all`), never reading the artifact's share fields, then compared against the committed artifact.

| horizon | coherent shares, derived from inputs | smallest | argmin pairing | committed `..._range[0]` | agree | class |
|---|---|---|---|---|---|---|
| `5_year` | `[13.0, 16.6, 51.7, 58.6, 63.8, 70.0]` | **13.0** | `meisKindblom1999` (5-y OS 0.90) × `masunaga2025_localized` (5-y DSS 0.913) | 13.0 | ✅ | PRIMARY |
| `10_year` | `[50.0, 50.0, 57.1, 57.1]` | **50.0** | `meisKindblom1999` (10-y OS 0.70) × `bishop2019` (10-y DSS 0.85) | 50.0 | ✅ | PRIMARY |

Units: per cent of that pairing's deaths. n = 12 and 6 pairings, exhaustive enumerations, not samples — there is no sampling uncertainty on these; the uncertainty lives in the published survival percentages, which carry **no stated interval** (W06e's registry audit, reused).

**W06e's stated 13.0 and 50.0 are confirmed. No discrepancy to report.** My independent enumeration also reproduces the committed integer counts (12 / 6 coherent / 6 impossible; 6 / 4 / 2).

### 2. The finding W06e did not state: the field is a re-label, not a new number

`cross_series()` computes `shares = sorted(...)` and already publishes `competing_share_of_deaths_pct_range = [shares[0], shares[-1]]`. **`smallest_coherent_share_pct` *is* `shares[0]`, so it is numerically identical to the range's lower bound, which is already committed.** I proved this by assertion on both horizons (§Validation, RUN 5).

So the answer to "what is the smallest readout" is sharper than expected: **the smallest readout adds zero new numbers.** The margin has been printed in the artifact since it was written; what was missing is that nobody reads a band's lower edge as a countdown to a gate. The patch's whole content is a **name and a comment** attached to a value already present. That is a weaker artifact than "we computed the margin", and I report it as such rather than dressing it up.

### 3. Is it correct? — Yes as a distance to the next flip; **not in general** a distance to the gate

This is the correction to the framing, and it is the substantive part of the answer.

- **Correct:** a coherent pairing becomes impossible exactly when its own competing share reaches zero, so the smallest coherent share is exactly the distance to **the next flip**. Confirmed by execution at both horizons (§Validation, RUN 3–4).
- **Not in general the gate distance:** the gate is *"most pairings impossible"*. One flip breaches it only when the horizon already sits at the boundary. For this committed file the two coincide at both horizons, but **for two different and non-transferable reasons**:
  - `5_year` sits at **6 of 12 — exactly the boundary** (W06c's structural point), so the single next flip carries it to 7/12 and breaches. Verified: 6→7 impossible.
  - `10_year` sits at 2 of 6, one pairing of slack, so one flip (3/6) would *not* breach — **it coincides only because the two smallest shares are tied at 50.0 and flip together**, taking it 2/6 → 4/6 in one step. Verified by execution: `OS10 = 0.8500` gives 2 impossible, `0.8505` gives **4** impossible.
- **Consequence, stated plainly:** alone, this field answers *"how far to the next flip"*. It answers *"how far to the gate"* only when read **together with the impossible count** — i.e. with W06d's `impossible_fraction`. The minimal honest readout is therefore the three fields together, not this one alone. I report that rather than overselling a single number.
- **It is not a countdown.** After the 5-year flip the smallest coherent share jumps **13.0 → 16.6** (the next pairing up), so the field resets upward at the moment it reaches zero. It is a distance to the nearest boundary from where you stand, not a monotone fuel gauge.
- **It is in share units, not input units** — which is precisely the defect W06e diagnosed in W06d's fields. Conversion is exact: *margin in percentage points of either survival input = share × that pairing's all-cause mortality*. 5-year: 13.0 % × 10.0 pp = **1.30 pp** (matches W06e's executed bracket). 10-year: 50.0 % × 30.0 pp = **15.0 pp** (matches my bracket below). **But the artifact does not expose the argmin pairing's all-cause mortality**, so a reader cannot perform that conversion from the artifact alone. The field is one denominator short of the units W06e asked for.

### 4. Execution verification of the closed form (`PRIMARY`; unmodified committed generator, real exit codes)

I perturbed exactly one numeric field of the committed inputs per run and re-ran the **unpatched** committed generator. No contamination model, no π, no parameter of my own — a raw perturbation of a committed input.

**5-year.** Prediction from the closed form: `smallest_coherent_share_pct` 13.0 of a 10.0 pp all-cause mortality ⇒ flip when `masunaga2025_localized` 5-y DSS falls below 0.9000 (1.30 pp below the committed 0.913). Verbatim `cross 5_year` stdout lines, every run `EXIT=0`:

| 5-y DSS | generator stdout, verbatim |
|---|---|
| **0.913** (committed) | `competing share [13.0, 70.0]% (median 58.6%), ceiling [8.7, 24.2] pts, 6/12 pairings coherent (6 impossible, 0 undefined)` |
| 0.9010 | `competing share [1.0, 65.9]% (median 52.9%), ceiling [9.9, 24.2] pts, 6/12 pairings coherent (6 impossible, 0 undefined)` |
| 0.9005 | `competing share [0.5, 65.7]% (median 52.6%), ceiling [10.0, 24.2] pts, 6/12 pairings coherent (6 impossible, 0 undefined)` |
| **0.9000** | `competing share [0.0, 65.5]% (median 52.4%), ceiling [10.0, 24.2] pts, 6/12 pairings coherent (6 impossible, 0 undefined)` ← last coherent, margin exhausted |
| **0.8995** | `competing share [16.6, 65.3]% (median 52.1%), ceiling [10.1, 24.2] pts, 5/12 pairings coherent (7 impossible, 0 undefined)` ← **flipped, and the gate is breached** |
| 0.8990 | `competing share [16.6, 65.2]% (median 51.9%), ceiling [10.1, 24.2] pts, 5/12 pairings coherent (7 impossible, 0 undefined)` |

The smallest share tracks the remaining margin exactly as it is spent: 13.0 → 1.0 → 0.5 → 0.0 → flip. That is the closed form confirmed by execution, not by algebra. At 7/12, W06d's `quotable_by_own_rule` would read `false`.

**10-year.** Prediction: 50.0 of a 30.0 pp all-cause mortality ⇒ flip when `meisKindblom1999` 10-y OS rises above 0.8500 (15.0 pp above the committed 0.70). Verbatim `cross 10_year` lines, every run `EXIT=0`:

| 10-y OS | generator stdout, verbatim |
|---|---|
| **0.70** (committed) | `competing share [50.0, 57.1]% (median 57.1%), ceiling [15.0, 15.0] pts, 4/6 pairings coherent (2 impossible, 0 undefined)` |
| 0.84 | `competing share [6.3, 57.1]% … 4/6 pairings coherent (2 impossible, 0 undefined)` |
| 0.8495 | `competing share [0.3, 57.1]% … 4/6 pairings coherent (2 impossible, 0 undefined)` |
| **0.8500** | `competing share [0.0, 57.1]% … 4/6 pairings coherent (2 impossible, 0 undefined)` ← last coherent |
| **0.8505** | `competing share [57.1, 57.1]% … 2/6 pairings coherent (**4 impossible**, 0 undefined)` ← **two pairings flip at once (the tie)** |
| 0.86 | `competing share [57.1, 57.1]% … 2/6 pairings coherent (4 impossible, 0 undefined)` |

Both flips land exactly where the closed form predicts. The 10-year run is also the direct evidence for §3's tie caveat.

### 5. The patch (returned inline, **NOT APPLIED** — I am read-only on the tree)

One functional line; the rest is the comment that makes the field readable without this report. Zero deletions, zero modifications.

```diff
--- a/research/manuscripts/emc_mortality_decomposition.py
+++ b/research/manuscripts/emc_mortality_decomposition.py
@@ -282,6 +282,18 @@
             "pairings_coherent": len(coherent),
             "pairings_impossible": len(impossible),
             "pairings_undefined": len(undefined),
+            # HOW CLOSE THIS HORIZON IS TO ITS OWN GATE, in one number. The gate is the
+            # rule stated in excluded_pairings.how_to_read_them: "A horizon where most
+            # pairings are impossible should not be quoted at all." A coherent pairing
+            # becomes impossible exactly when its own competing share reaches zero, so the
+            # SMALLEST coherent share is the distance to the next flip. It is a distance,
+            # not a direction: it says nothing about whether any input is wrong, and
+            # nothing about which way any input would move. To read it in the units of the
+            # survival percentages themselves, multiply by that pairing's all-cause
+            # mortality. Numerically identical to competing_share_of_deaths_pct_range[0];
+            # emitted under its own name because the range is read as a band and a band is
+            # not read as a margin.
+            "smallest_coherent_share_pct": shares[0] if shares else None,
             "competing_share_of_deaths_pct_range": [shares[0], shares[-1]] if shares else None,
             "competing_share_of_deaths_pct_median": (
                 shares[len(shares) // 2] if shares else None
```

It is placed with the pairing counts rather than with the band, deliberately: read next to `pairings_impossible` it is a margin; read next to the range it disappears into the band it duplicates.

The regenerated `emc-mortality-decomposition.json` follows from re-running the generator and must **not** be hand-edited (generated-output convention). Its complete diff is two inserted lines:

```diff
@@ -87,6 +87,7 @@
    "pairings_coherent": 6,
    "pairings_impossible": 6,
    "pairings_undefined": 0,
+   "smallest_coherent_share_pct": 13.0,
    "competing_share_of_deaths_pct_range": [
@@ -155,6 +156,7 @@
    "pairings_coherent": 4,
    "pairings_impossible": 2,
    "pairings_undefined": 0,
+   "smallest_coherent_share_pct": 50.0,
    "competing_share_of_deaths_pct_range": [
```

**This patch is orthogonal to W06d's** — different insertion point, no shared lines — but the two are complementary, not alternatives (§3): the impossible fraction says whether the next flip breaches the gate; this says how far the next flip is.

### 6. The paper quotes no cross-series figure — verified myself, not taken from W06e

```
$ grep -n -E '58\.6|70\.0|13\.0|\[13|cross.series|cross-series|pairings' \
      research/manuscripts/emc-mortality-mechanisms-paper.md
(no output)
$ grep -n -E '57\.1|50\.0' research/manuscripts/emc-mortality-mechanisms-paper.md
(no output)
$ grep -n -i -E 'five-year|5-year|five year' research/manuscripts/emc-mortality-mechanisms-paper.md
262:…a selection signal in a 42-patient cohort reporting 100 per cent five-year survival…
398:…treated the World Health Organization indicator nMx as a five-year probability…
```
Neither hit is a cross-series figure. A tracked `git grep '58.6'` outside the campaign directory returns the artifact itself plus unrelated ASO/HLA/PDB coordinate matches. **The paper quotes nothing this patch touches.** I did not edit the paper.

## Validation evidence

Environment for every command: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `python3` 3.11.15 stdlib only, working directory `/tmp/claude-0/w06f/`, **no network used**. Repository read at `ce743d6` / `4ec9da1` / `a87275c`, inputs verified byte-identical across both moves.

**RUN — 1. The control. Unpatched generator reproduces the committed artifact byte-identically.**
```
$ cd /tmp/claude-0/w06f/base && python3 research/manuscripts/emc_mortality_decomposition.py
wrote research/manuscripts/emc-mortality-decomposition.json
  DIRECT  Japanese national registry, localised surgical: 4/13 deaths were not EMC deaths = 30.8% (ceiling 6.7 pts)
  DIRECT  Japanese national registry, metastatic at diagnosis: 1/10 deaths were not EMC deaths = 10.0% (ceiling 31.0 pts)
  within  Meis-Kindblom 1999 pathology series: at 10y, 39.4% of deaths were not EMC deaths (antitumour ceiling 18.2 pts)
  cross   5_year: competing share [13.0, 70.0]% (median 58.6%), ceiling [8.7, 24.2] pts, 6/12 pairings coherent (6 impossible, 0 undefined)
  cross   10_year: competing share [50.0, 57.1]% (median 57.1%), ceiling [15.0, 15.0] pts, 4/6 pairings coherent (2 impossible, 0 undefined)
  background check: RUN
  BG localised: observed 3.0% vs background 3.1% -> ratio 0.97 (95% CI 0.38-2.41)
  BG metastatic: observed 3.4% vs background 3.3% -> ratio 1.04 (95% CI 0.18-5.18)
GEN_EXIT=0
$ cmp /tmp/claude-0/w06f/committed.json research/manuscripts/emc-mortality-decomposition.json
CMP_EXIT=0
$ md5sum …
19ef9f55b2ff4c1f6eb2dab62f8b2526  /tmp/claude-0/w06f/committed.json
19ef9f55b2ff4c1f6eb2dab62f8b2526  research/manuscripts/emc-mortality-decomposition.json
```
**The comparison in RUN 6 therefore has a control.**

**RUN — 2. Independent derivation from the inputs** (`derive.py`, exit 0). Output quoted in Result §1, including `IDENTITY CHECK smallest == range[0] : True` at both horizons.

**RUN — 3 & 4. The twelve perturbation runs** (`sweep.sh`) against the **unmodified** committed generator. Every run `EXIT=0`; tables in Result §4 are verbatim generator stdout. The generator's `verify_provenance` gate passed on every run — I perturbed only numeric survival fields and touched no `registry_verbatim` string.

**RUN — 5 & 6. Patched generator, and proof it changes nothing.**
```
$ cd /tmp/claude-0/w06f/patched && python3 research/manuscripts/emc_mortality_decomposition.py
GEN_EXIT=0
$ cmp out_base.txt out_patched.txt          # stdout of control vs patched run
STDOUT_CMP_EXIT=0                            # byte-identical, all nine lines
$ diff -u committed.json patched/…/emc-mortality-decomposition.json | grep -c '^-[^-]'
0                                            # zero removed or modified lines
$ python3  [strips exactly {smallest_coherent_share_pct} from each horizon and compares]
  5_year: existing keys identical and in identical order; smallest_coherent_share_pct=13.0
  10_year: existing keys identical and in identical order; smallest_coherent_share_pct=50.0
PROVED: candidate == committed field-for-field after removing exactly 1 key per horizon; nothing else changed
PROVED: the emitted value equals competing_share_of_deaths_pct_range[0] at both horizons (it is a re-label, not a new number)
PROOF_EXIT=0
```
The assertions cover: the key present on every horizon; the stripped horizon dict equal **and in identical key order** to the committed one; the whole document equal outside `cross_series`; and the re-label identity. Any failure would have raised.

**RUN — 7. Existing test module against the patched generator.**
```
$ python3 -m pytest research/manuscripts/tests/test_emc_mortality_decomposition.py -q
/usr/local/bin/python3: No module named pytest
PYTEST_EXIT=1
```
`pytest` is **not installed in this container** — an honest tooling gap, **not a pass**. Substitute (same approach W06d recorded): the module uses no fixtures, marks or parametrisation, so I stubbed the `pytest` import and called every `test_*` function directly. That runner is **weaker** than pytest — no assertion rewriting, no collection-error reporting — and this result is not a substitute for the repository's real gate.
```
$ python3 /tmp/claude-0/w06f/stubrun.py
PASS test_a_genuine_zero_over_zero_is_undefined_rather_than_impossible
… (19 lines, all PASS; includes test_the_reported_band_excludes_impossible_pairings_and_counts_them,
   test_every_pairing_is_enumerated_not_just_the_extremes,
   test_the_committed_artifact_carries_no_negative_or_impossible_headline)
19/19 passed, 0 failed
TESTS_EXIT=0
```
The two `test_the_committed_artifact_*` tests read the artifact inside the patched sandbox, i.e. the **candidate** JSON, so they confirm the candidate still satisfies the committed artifact's own guards.

**RUN — 8. Tree untouched, HEAD-move safety.**
```
$ git status --porcelain          (start and end)   -> no output
$ git diff --stat ce743d6 a87275c -- <my six files> -> empty, EXIT=0
$ git diff --stat 4ec9da1 a87275c -- <my six files> -> empty, EXIT=0
```

**PROPOSED (NOT RUN):**
- `scripts/preflight.sh` and the repository's real pytest gate on the patched generator. Blocked by the missing `pytest` and by my read-only constraint; my dispatch does not authorise preflight. The generator's owner must run it.
- A guard test asserting the field's value on the committed artifact. **Deliberately not authored** — a build-failing guard is an acceptance criterion, and COMMON-BRIEF §2 bars me from writing my own.
- Emitting the argmin pairing's all-cause mortality so the share converts to percentage points inside the artifact (§3's one-denominator gap). Nominated, not written — it is a second field and my dispatch asked for the smallest change.

## Limitations

- **What the readout does not do, stated plainly, as the dispatch requires.** It is a **distance, not a direction of travel**: it says how far the nearest pairing sits from flipping, and nothing about which way any input would move, how likely any move is, or whether a move is happening. It **asserts nothing about whether any committed input is wrong** — no survival percentage, no cohort, no attribution is called into question by it, and a small margin is not evidence of error in the number that produces it. It is not a probability, not an interval, and not an uncertainty estimate.
- **It is not in general the distance to the gate** (§3). It is the distance to the *next flip*; the two coincide in this committed file at 5 years by boundary position and at 10 years by a numerical tie, and either coincidence disappears if a series is added or removed. Read it with `pairings_impossible`, never alone.
- **It adds no number** — it duplicates `competing_share_of_deaths_pct_range[0]`, which has always been committed. The contribution is a name and a comment, and it should be judged as that.
- **It is one denominator short of W06e's units.** Converting 13.0 % to the 1.30 pp that actually moves needs the argmin pairing's all-cause mortality, which the artifact does not expose.
- **Not applied.** I am read-only; the patch is routed to the generator's owner. Nothing is merged; the committed artifact at `a87275c` carries neither this field nor W06d's two.
- **The underlying inputs carry no stated uncertainty.** As W06e established and I did not re-audit, the registry states no confidence interval on any survival percentage, so a margin of "1.30 pp" is measured against nothing. Its apparent tightness is not comparable to a margin measured against a real interval.
- **`pytest` unavailable**; 19/19 comes from a weaker hand-rolled runner. Not the repository's gate.
- **No clinical claim.** This is arithmetic on published summary percentages across heterogeneous studies. Nothing here bears on diagnosis, prognosis, treatment selection or clinical practice; it establishes no efficacy, safety, selectivity or clinical readiness; and `systems/POLICY-evidence.md` §2.4–2.5 apply in full to every figure quoted. The decomposition's own directional bias (the competing share is an **under**-estimate) is unchanged by this patch.
- Single-worker analysis; my derivation was not independently replicated beyond the executed runs.

## Tool-call and wall-clock count actually used

**29 tool calls** (all Bash) against a ~40 target. **Wall clock 02:58:52Z → 03:03:01Z = 4 minutes 9 seconds** against a ~40 min target. Nothing padded, nothing left running, no background jobs.

## Next concrete action

**Route the three fields as one decision, and then close lane 6's cross-series thread.** W06d's `impossible_fraction` / `quotable_by_own_rule` and this report's `smallest_coherent_share_pct` are complementary halves of one readout — §3 shows neither answers "how close to the gate" alone — and they touch adjacent lines of the same dict, so applying them separately risks a conflicting hand-merge of generated output. The concrete task for the generator's owner: apply both patches in one change, regenerate, and run `scripts/preflight.sh` (which I could not).

**I nominate no further lane-6 analytic worker, and the reason is substantive rather than exhaustion.** The cross-series block has now been swept (W06c), had its gate made machine-readable (W06d), had its margin ranked against every other conclusion in the lane (W06e), and had that margin verified and its correctness bounded (here) — and the block is **not quoted in the paper at all**, which my own grep confirms. Further work on it would be instrumentation of an internal number that nothing published depends on. The one remaining open item is a **decision, not an analysis**: whether a horizon at exactly half should stay quotable, which W06d correctly refused to take and which no worker may take under COMMON-BRIEF §2.
