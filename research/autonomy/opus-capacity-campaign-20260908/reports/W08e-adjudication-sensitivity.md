> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Start `date -u`: `Tue Sep  8 02:31:17 UTC 2026` · End `date -u`: `Tue Sep  8 02:33:0x UTC 2026` (exact end printed below)

---

# W08e — Adjudication-sensitivity of the EMC interval census

## Worker

Worker ID **W08e**, lane 8 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT ONLY, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). I did not and cannot observe the served model; no environment variable in this container names a model at all. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:31:17 UTC 2026`
`date -u` at end: `Tue Sep  8 02:32:16 UTC 2026` (last recorded probe; the report was drafted after this, no further commands run)

Repository read: `/home/user/Rare-cancers`, **actual HEAD read = `47aac85f874a57a6f981c3432abcf16980968aec`**. Note this is *not* the `92abbcb905cacf07f14b238db50d1b98f6590374` named in `COMMON-BRIEF.md`; the checkout has moved. `git status --porcelain` printed nothing (clean tree). I also read the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/` (read-only, not overlaid, not copied). **No writes of any kind to the Git working tree; no git write operations; no network.**

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`:

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

**How much of the EMC interval census is produced by adjudication judgement rather than by evidence?** Concretely: recompute the union census's descriptive statistics under each of the three rule variants W08c flagged, separately, as an explicit sensitivity table, and state which conclusions survive every variant.

This is open because W08c's own report names twelve borderline calls and explicitly says at least two of them ("the single most consequential borderline call in this pass", and the osseous-EMC call which "carries real weight") would change the numbers — but it computed statistics under one rule set only. Nobody has quantified the spread. No new retrieval was performed and none was needed.

## Prior-work check

Commands actually run (all read-only):

```
$ git rev-parse HEAD
47aac85f874a57a6f981c3432abcf16980968aec
$ git status --porcelain | head -20     # (empty)
$ git ls-files | grep -i -E "sensitiv|census" | head -15
```
→ 15 paths, of which the only interval-census one is `research/autonomy/opus-capacity-campaign-20260908/reports/W08b-interval-census-adjudication.md`. The rest are unrelated (`ternary-system-census.yml`, modality/ASO/review-seat censuses, `W06b-misclassification-sensitivity.md`, `research/literature/emc-km-reachability-census-2026-08-25.json`).

```
$ rg -l -i "sensitivity" --glob '!.git' research/autonomy/opus-capacity-campaign-20260908/ | head -10
```
→ W02b, W17b, W19, W06b, W02c, W06c, W08, W17, W06, W19b. None is an adjudication-rule sensitivity analysis of the interval census; W06b is a *misclassification* sensitivity in the diagnostic-delay lane, a different question.

```
$ rg -l -i -e "10469211" -e "22743288" --glob '!.git' | head
research/literature/rt-lung-mets-probe.json
research/literature/fusion-consensus-probe.json
research/autonomy/opus-capacity-campaign-20260908/reports/W08-disease-course-surveillance-question.md
research/autonomy/opus-capacity-campaign-20260908/reports/W08b-interval-census-adjudication.md
research/autonomy/opus-capacity-campaign-20260908/reports/W08c-blinded-third-adjudication.md
research/autonomy/opus-capacity-campaign-20260908/reports/W10b-older-literature-sweep.md
research/modalities/nr4a3-nuccore-sweep-inputs.json
$ grep -rl -e "10469211" -e "22743288" /tmp/claude-0/frozen-corpus/extracted/corpus/ | head
/tmp/claude-0/frozen-corpus/extracted/corpus/research/literature/fusion-consensus-probe.json
/tmp/claude-0/frozen-corpus/extracted/corpus/research/literature/rt-lung-mets-probe.json
/tmp/claude-0/frozen-corpus/extracted/corpus/research/modalities/nr4a3-nuccore-sweep-inputs.json
EXIT=0
```
The two variant PMIDs appear in the lane-8 reports and in two probe JSONs, never in a sensitivity computation. **This analysis is not a replay.** Confirmed not replayed from `CLOSED-WORK.md`: no publisher/PMC/EuropePMC/institutional route was attempted at all (no network was used); PUB-EMC-CLASSIFICATION was not touched; no Brenca route; no pooling with `emc-km-reachability-census-2026-08-25.json` (not opened); no restricted review recreated.

**Transfer gap, stated honestly:** `reports/W08d-*.md` **does not exist on disk at HEAD `47aac85`** — `ls reports/ | grep -i W08d` returned nothing, `grep -rl "W08d"` over the tree and over the frozen corpus returned nothing. The coordinator has not yet written it. I therefore could **not** read W08d. Its one load-bearing input — PMID 36097623 converted from UNKNOWN to a Column A event at **108 months** — is taken **verbatim from my dispatch prompt** and is marked SECONDARY (TRANSFERRED, unread source) throughout. I searched the repository for independent corroboration of that interval: `research/manuscripts/emc-terminal-events.json` and `emc-terminal-events-classified.json` both carry PMID 36097623, but only a terminal-event quote ("…development of further metastases ultimately resulting in death"), **with no interval**. So 108 months is not independently corroborated inside this repository, and I did not retrieve anything to check it.

Arithmetic cross-check that the transferred baseline is what my dispatch says: my dispatch states variant 2 takes union Column A from n=9 to n=7 and Column B from n=5 to n=4. Removing 23588370's events (A: 26, 74; B: 36) from W08c's sets plus one added Column A event reproduces exactly 9→7 and 5→4. The baseline union is therefore W08c's sets with 108 appended to Column A, and nothing else. This is consistent, not independent confirmation.

## Method / inputs

- **No retrieval of any kind. No network. No new sources.** All inputs are transferred values already adjudicated by W08c (read from `reports/W08c-blinded-third-adjudication.md` at HEAD `47aac85`) plus the single transferred W08d value.
- Quartile estimator: **W08c's exact estimator, copied verbatim** from the `stats.py` reproduced in W08c's Validation-evidence section — linear interpolation on order statistics, `h=(n-1)p`, `x[⌊h⌋] + (h-⌊h⌋)(x[⌈h⌉]-x[⌊h⌋])`. Median via `statistics.median`. Threshold counts are **strictly** greater than 24/60/120 months, as W08c defined them.
- Baseline union sets (months):
  - Column A (first distant or regional metastasis): `[10, 16, 24, 26, 34, 48, 60, 74, 108]` — W08c A1–A8 (PMIDs 9158707, 35494187, 30534357, 23588370, 10450885, 18308379, 9711893, 23588370) plus 36097623 at 108 (TRANSFERRED from W08d, unread).
  - Column B (first local recurrence): `[16, 29, 36, 42, 168]` — W08c B1–B5 (PMIDs 12181708, 38111543, 23588370, 10469211, 15810095).
- Variant construction, each applied **alone** to the baseline, never combined:
  1. **V1 — admit PMID 10469211's two unanchored values.** W08c verbatim: *"Three patients had metastases, one at 12 weeks, one at 10 months, and one at presentation of recurrent tumour."* Adds **2.8** (12 weeks, at 30.44 d/mo ≈ 2.76, reported 2.8 per dispatch) and **10** months to Column A. Column B unchanged.
  2. **V2 — exclude EMC arising primarily in bone** (PMIDs 23588370, 28249774, 9149016). Only 23588370 contributes included events: removes **26** and **74** from Column A and **36** from Column B. (28249774 and 9149016 contribute no included events — 28249774 appears only among W08c's imprecise/bounded records.)
  3. **V3 — admit PMID 22743288**, the combined synovial sarcoma + EMC carrying both SS18-SSX2 and EWSR1-NR4A3. W08c verbatim: *"The tumor recurred 7 years after the initial diagnosis"* → a local recurrence at **84** months, added to Column B. Column A unchanged.
- Execution: `/tmp/claude-0/w08e/sens.py`, Python 3.11.15, Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w08e` — outside the Git tree.

## Result

Units are **months**. Every `n` and every `>t` figure is a **count of published case-report events**. None is a rate, risk, incidence, cumulative incidence or probability. **The frame has no denominator.** UNKNOWN records (5/84 unavailable abstracts, less the one W08d converted) remain excluded and are never imputed. Anchors are **heterogeneous and unharmonised** — Column A mixes primary surgery, initial diagnosis, primary detection and "definitive therapy"; Column B mixes initial surgery, primary resection, initial diagnosis and "definitive therapy" — so these are not one clock, and the quartiles below are descriptive summaries of a mixed-anchor list, not estimates of any single quantity.

### Sensitivity table — Column A (first distant or regional metastasis)

| Rule set | Row class | n (events) | min | Q1 | median | Q3 | max | >24 mo | >60 mo | >120 mo |
|---|---|---|---|---|---|---|---|---|---|---|
| **Baseline** (W08c + W08d 36097623@108) | PRIMARY + 1 SECONDARY(transferred) | 9 | 10 | 24.00 | 34.00 | 60.00 | 108 | 6 of 9 | 2 of 9 | 0 of 9 |
| **V1** admit 10469211 unanchored (2.8, 10) | PRIMARY (anchor UNKNOWN for the 2 added) | 11 | 2.8 | 13.00 | 26.00 | 54.00 | 108 | 6 of 11 | 2 of 11 | 0 of 11 |
| **V2** exclude osseous-primary EMC | PRIMARY + 1 SECONDARY(transferred) | 7 | 10 | 20.00 | 34.00 | 54.00 | 108 | 4 of 7 | 1 of 7 | 0 of 7 |
| **V3** admit 22743288 (combined SS+EMC) | unchanged from baseline | 9 | 10 | 24.00 | 34.00 | 60.00 | 108 | 6 of 9 | 2 of 9 | 0 of 9 |

### Sensitivity table — Column B (first local recurrence)

| Rule set | Row class | n (events) | min | Q1 | median | Q3 | max | >24 mo | >60 mo | >120 mo |
|---|---|---|---|---|---|---|---|---|---|---|
| **Baseline** | PRIMARY | 5 | 16 | 29.00 | 36.00 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |
| **V1** | unchanged from baseline | 5 | 16 | 29.00 | 36.00 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |
| **V2** exclude osseous-primary EMC | PRIMARY | 4 | 16 | 25.75 | 35.50 | 73.50 | 168 | 3 of 4 | 1 of 4 | 1 of 4 |
| **V3** admit 22743288 @ 84 mo | PRIMARY (histology mixed) | 6 | 16 | 30.75 | 39.00 | 73.50 | 168 | 5 of 6 | 2 of 6 | 1 of 6 |

Each variant is reported **alongside** the baseline and never in place of it. They are **not** to be combined into a single "corrected" census; W08c's and W08d's sets are not revised by this report.

### Which conclusions survive every variant — and which do not

**Stable across the baseline and all three variants (STABLE):**

- Column A contains **no documented event beyond 120 months** (0 in every variant), and its **maximum is 108 months** in every variant. Whether the census's longest first-metastasis event is beyond ten years does not turn on any of the three calls. (It does turn entirely on the one transferred, unread W08d value — see Limitations.)
- Column A's **median stays inside 26–34 months** in every variant, i.e. between roughly two and three years.
- Column B's **minimum is 16 months** and its **maximum is 168 months** in every variant, and **exactly one Column B event exceeds 120 months** in every variant.
- Column B's **median stays inside 35.5–39 months** in every variant — the narrowest band in the whole table.
- **A clear majority of Column B events exceeded 24 months** in every variant (4/5, 4/5, 3/4, 5/6).
- Both columns remain **small, single-digit-to-low-double-digit event counts** under every rule (A: 7–11; B: 4–6). No variant makes the census large.

**Not stable — these depend on the adjudication call, not on the evidence (UNSTABLE):**

- **The shortest documented Column A interval.** 10 months at baseline and under V2/V3, **2.8 months** under V1 — a factor of ~3.6, produced entirely by whether one sentence's missing anchor is inferred. Any statement about how early a first metastasis has been documented is a judgement call, not a finding.
- **Column A's lower quartile.** 24.00 (baseline, V3) / 13.00 (V1) / 20.00 (V2) — an 11-month spread, i.e. the Q1 moves by more than the entire baseline interquartile position of the earliest events.
- **"Most Column A events occurred beyond 24 months."** True at baseline and V3 (6 of 9) and under V2 (4 of 7), but **false under V1 (6 of 11)**. A single admissibility call flips this from a majority statement to a minority one. It must not be asserted without naming the rule.
- **Column A's median as a specific number.** 34 (baseline, V2, V3) vs 26 (V1) — an 8-month, ~24% shift from one call.
- **Column A's upper quartile.** 60.00 vs 54.00 depending on the call.
- **Column B's upper quartile.** 42.00 at baseline/V1, **73.50** under both V2 and V3 — a 31.5-month swing, and notably it moves the same way whether an event is *removed* (V2) or *added* (V3), because both change which order statistics the interpolation lands on in a 4–6 element list.
- **Column B's count beyond 60 months.** 1 at baseline/V1/V2, **2** under V3.
- **The census size itself.** n is a product of adjudication as much as of the literature: Column A ranges 7–11 (a 57% spread relative to its smallest value) and Column B 4–6 (50%), across three single, individually defensible calls.

**Overall answer to the question posed.** In this census the *ordering and the extremes* are largely evidence-driven, and the *central tendency* is fairly robust (Column A median within 26–34 months, Column B median within 35.5–39 months across every variant). But **the quartiles, the minimum of Column A, the threshold counts, and n itself are substantially adjudication-driven**: with 4–11 events per column, a single inclusion decision moves a quartile by up to 31.5 months and can invert a majority statement. Any use of these numbers must therefore quote the rule set alongside the value. The one variant that changes the most is **V1**, exactly as W08c predicted when it flagged 10469211 as "the single most consequential borderline call in this pass" — that prediction is confirmed quantitatively here.

**No surveillance interval, imaging schedule, follow-up duration or clinical recommendation is stated, implied or derivable from anything above.** These are counts of published case reports without a denominator; they cannot support one, and none should be constructed from them.

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24 x86_64; `Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]`; cwd `/tmp/claude-0/w08e` (outside the Git tree, nothing written under `/home/user/Rare-cancers`).

Script `/tmp/claude-0/w08e/sens.py`, reproduced in full (the `q()` function is W08c's verbatim):

```python
import statistics as st

def q(x,p):
    x=sorted(x); n=len(x); h=(n-1)*p; lo=int(h); hi=min(lo+1,n-1)
    return x[lo]+(h-lo)*(x[hi]-x[lo])

def row(label, col, v):
    v=sorted(v)
    beyond={t:sum(1 for x in v if x>t) for t in (24,60,120)}
    print(f"{label:<42} | {col} | n={len(v):<2} | values={v}")
    print(f"{'':42} |   | min={min(v):<6} Q1={q(v,.25):<7.2f} median={st.median(v):<7.2f} Q3={q(v,.75):<7.2f} max={max(v)}")
    print(f"{'':42} |   | >24mo: {beyond[24]} of {len(v)}   >60mo: {beyond[60]} of {len(v)}   >120mo: {beyond[120]} of {len(v)}   (counts of published events)")
    print()

# BASELINE union census (W08c blinded sets + W08d's converted PMID 36097623 at 108 mo)
A_base=[10,16,24,26,34,48,60,74,108]   # first distant/regional metastasis, months
B_base=[16,29,36,42,168]               # first local recurrence, months

# V1: admit PMID 10469211's two unanchored values (12 weeks = 2.8 mo; 10 mo) into Column A
A_v1 = A_base + [2.8,10]
B_v1 = list(B_base)

# V2: exclude EMC arising primarily in bone -> drops 23588370's A events (26,74) and B event (36)
A_v2 = [x for x in A_base]; A_v2.remove(26); A_v2.remove(74)
B_v2 = [x for x in B_base]; B_v2.remove(36)

# V3: admit PMID 22743288 (combined SS+EMC), local recurrence 7 years after initial diagnosis = 84 mo
A_v3 = list(A_base)
B_v3 = B_base + [84]

for label,(A,B) in [
  ("BASELINE (union, W08c+W08d)",(A_base,B_base)),
  ("V1 admit 10469211 unanchored (2.8,10)",(A_v1,B_v1)),
  ("V2 exclude osseous-primary EMC",(A_v2,B_v2)),
  ("V3 admit 22743288 combined SS+EMC",(A_v3,B_v3)),
]:
    row(label,"A",A)
    row(label,"B",B)

print("Every n and every '>t months' figure is a COUNT OF PUBLISHED CASE-REPORT EVENTS.")
print("No rate, risk, incidence or probability. The frame has NO denominator.")
print("Anchors are heterogeneous and unharmonised. UNKNOWN records excluded, never imputed.")
```

Verbatim output of `$ cd /tmp/claude-0/w08e && python3 sens.py; echo "EXIT=$?"`:

```
BASELINE (union, W08c+W08d)                | A | n=9  | values=[10, 16, 24, 26, 34, 48, 60, 74, 108]
                                           |   | min=10     Q1=24.00   median=34.00   Q3=60.00   max=108
                                           |   | >24mo: 6 of 9   >60mo: 2 of 9   >120mo: 0 of 9   (counts of published events)

BASELINE (union, W08c+W08d)                | B | n=5  | values=[16, 29, 36, 42, 168]
                                           |   | min=16     Q1=29.00   median=36.00   Q3=42.00   max=168
                                           |   | >24mo: 4 of 5   >60mo: 1 of 5   >120mo: 1 of 5   (counts of published events)

V1 admit 10469211 unanchored (2.8,10)      | A | n=11 | values=[2.8, 10, 10, 16, 24, 26, 34, 48, 60, 74, 108]
                                           |   | min=2.8    Q1=13.00   median=26.00   Q3=54.00   max=108
                                           |   | >24mo: 6 of 11   >60mo: 2 of 11   >120mo: 0 of 11   (counts of published events)

V1 admit 10469211 unanchored (2.8,10)      | B | n=5  | values=[16, 29, 36, 42, 168]
                                           |   | min=16     Q1=29.00   median=36.00   Q3=42.00   max=168
                                           |   | >24mo: 4 of 5   >60mo: 1 of 5   >120mo: 1 of 5   (counts of published events)

V2 exclude osseous-primary EMC             | A | n=7  | values=[10, 16, 24, 34, 48, 60, 108]
                                           |   | min=10     Q1=20.00   median=34.00   Q3=54.00   max=108
                                           |   | >24mo: 4 of 7   >60mo: 1 of 7   >120mo: 0 of 7   (counts of published events)

V2 exclude osseous-primary EMC             | B | n=4  | values=[16, 29, 42, 168]
                                           |   | min=16     Q1=25.75   median=35.50   Q3=73.50   max=168
                                           |   | >24mo: 3 of 4   >60mo: 1 of 4   >120mo: 1 of 4   (counts of published events)

V3 admit 22743288 combined SS+EMC          | A | n=9  | values=[10, 16, 24, 26, 34, 48, 60, 74, 108]
                                           |   | min=10     Q1=24.00   median=34.00   Q3=60.00   max=108
                                           |   | >24mo: 6 of 9   >60mo: 2 of 9   >120mo: 0 of 9   (counts of published events)

V3 admit 22743288 combined SS+EMC          | B | n=6  | values=[16, 29, 36, 42, 84, 168]
                                           |   | min=16     Q1=30.75   median=39.00   Q3=73.50   max=168
                                           |   | >24mo: 5 of 6   >60mo: 2 of 6   >120mo: 1 of 6   (counts of published events)

Every n and every '>t months' figure is a COUNT OF PUBLISHED CASE-REPORT EVENTS.
No rate, risk, incidence or probability. The frame has NO denominator.
Anchors are heterogeneous and unharmonised. UNKNOWN records excluded, never imputed.
EXIT=0
```

**Estimator-agreement check (RUN, implicit):** the baseline Column B row reproduces W08c's published Column B row exactly (n=5, min 16, Q1 29.00, median 36, Q3 42.00, max 168; 4/5, 1/5, 1/5), and the baseline Column A differs from W08c's published Column A only by the single transferred added value. This confirms the estimator was carried over correctly rather than reimplemented differently.

**PROPOSED (NOT RUN):** none. No repository test suite, no `scripts/preflight.sh`, no lint — this worker is read-only on the tree and its dispatch did not call for them. No content-policy refusal was encountered on any branch.

## Limitations

- **No new evidence was produced.** This is a re-computation over already-adjudicated values. It cannot make the census more complete, only make its dependence on rules visible.
- **W08d's report could not be read** — it is absent from the tree at HEAD `47aac85` and from the frozen corpus. The 108-month Column A value for PMID 36097623 is taken from the dispatch prompt only, is uncorroborated inside this repository, and is **load-bearing for one "stable" conclusion**: the statement that Column A's maximum is 108 months and that no Column A event exceeds 120 months rests entirely on that single unread transferred value. If it is wrong, that conclusion is wrong in every row of the table. Marked SECONDARY (TRANSFERRED).
- **These are counts of published case-report events, not population quantities.** Publication bias in a case-report frame is severe and one-directional; the direction is known, the magnitude is not.
- **The frame has no denominator.** No figure here is a rate, risk, incidence or probability, and none supports a survival or hazard estimate. Column A and Column B are not complementary and were not combined. Nothing here was pooled with any cohort-level median in this repository.
- **Anchors are heterogeneous and unharmonised** across and within both columns; quartiles computed over a mixed-anchor list are descriptive of that list only.
- **Competing risks are unobserved** — patients who died, were lost to follow-up, or whose follow-up ended before an event are invisible.
- **UNKNOWN records remain excluded and were never imputed.** The remaining unavailable abstracts are undercounts of unquantified size, not zeros.
- **Quartiles on 4–11 values are unstable by construction**, independent of the rule question. No confidence interval is quoted because there is no sampling frame; one would be uninterpretable.
- The three variants are **illustrative of the flagged calls, not exhaustive** — W08c documented twelve borderline calls and only three were tested. The true adjudication-dependence of this census is at least as large as shown, plausibly larger.
- **No surveillance interval, imaging schedule or clinical recommendation is stated or derivable here.**
- **Model identity is self-reported and unverified.**

## Stop condition

**MET.** A sensitivity table covering the baseline plus all three variants, for both Column A and Column B, with n / min / Q1 / median / Q3 / max and the counts beyond 24/60/120 months under W08c's exact quartile estimator, computed by a real command with quoted environment, verbatim output and **exit code 0**; plus an explicit statement of which conclusions survive every variant and which do not. No new retrieval, no new sources, no network. W08c's and W08d's sets were not revised.

## Tool-call and wall-clock count actually used

**8 tool calls** (all Bash; no ToolSearch, no PubMed, no network). Wall clock 02:31:17 → 02:33 UTC, approximately **2 minutes** of tool time — well inside the ~40 minute / ~40 call target.

## Next concrete action

One successor for this lane: **extend this sensitivity frame from three calls to all twelve** of W08c's documented borderline calls, computing a per-call leave-one-decision-out table (each call flipped alone against the baseline) plus the two extreme envelopes — the most-inclusive rule set and the most-exclusive rule set — to bound how wide the census can be made without violating any single stated rule. That requires no retrieval and no new sources, uses only values already written down in `W08c-blinded-third-adjudication.md`, and would convert "the quartiles are adjudication-driven" from a demonstration on three calls into a bounded envelope over the whole rule surface. A prerequisite the coordinator should clear first: **write `reports/W08d-*.md` to disk**, since the 108-month value it contributes is currently load-bearing and unreadable by any successor.
