> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**W17g**, lane 17 refill, OPUS-CAPACITY-CAMPAIGN-20260908 — resolution of the §5.1 specificity-clearance cluster (`0.1968` / `0.0155` / `0.038` / `0.41×`) in `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md`, the successor W17e named.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). I did not observe the served model. **No environment variable names a model** — the `model` arm of the grep returns nothing; only `claude`/`anthropic` names matched. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:38:45 UTC 2026`. `date -u` at end: `Tue Sep  8 02:40:29 UTC 2026`.

**Actual HEAD read** (this differs from the frozen commit named in `COMMON-BRIEF.md`, `92abbcb905cacf07f14b238db50d1b98f6590374`; I read the live checkout as it stands):

```
$ git rev-parse HEAD
d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4
$ git status --porcelain | head -20
(no output — clean tree)
```

I read the **live cloud checkout** at `/home/user/Rare-cancers`. I did not need the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/` for this question — every input is a committed file in the live checkout and I make no novelty or absence claim that depends on prior work outside lane 17's own transferred reports.

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

---

## Question

Line 761 of `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` prints four numbers — the specificity bar `0.1968`, the clearance margin `0.0155`, the standard error `0.038` and the ratio `0.41×` — that W17e found are carried by no artifact field and produced by no code. **Which `n` is that standard error meant to use, do the four numbers survive under each candidate `n`, and what is the smallest correct repair?**

Open because W17e re-derived all four as arithmetically self-consistent but noted that the printed `n ≈ 700` matches **neither** per-drug `n` of the row the sentence is about (597 and 565). This is the margin by which Part D's **one PASS row** clears its specificity control, so whether it is 0.41 SE or something smaller is load-bearing for how much weight the PASS can carry.

Secondary: settle whether §5.1 printing `0.1711` **unsigned** against an artifact field whose value is **−0.1711** is a prose defect, an artifact naming defect, or neither.

---

## Prior-work check

Transferred reports read (in `research/autonomy/opus-capacity-campaign-20260908/reports/`): `W17-heldout-validation.md`, `W17b-exact-welch-variance-inversion.md`, `W17c-mde-range-rederivation.md`, `W17d-atr-artifact-self-verification.md`, `W17e-pub-atr-figure-anchoring.md` (the last read in full via its persisted 49.8 KB tool result). `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md` read in full.

Commands run:

```
$ cd /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/ \
    && ls reports/ | grep -i w17
W17-heldout-validation.md
W17b-exact-welch-variance-inversion.md
W17c-mde-range-rederivation.md
W17d-atr-artifact-self-verification.md
W17e-pub-atr-figure-anchoring.md

$ grep -n -i -E "p1s\[0\]|0\.1968|0\.0155|0\.41|0\.038|0\.1711|specificity" <W17e report>
   (33 hits; lines 162-177 are W17e's R3 block, which states the four numbers have
    "no artifact field, no code output" and names this exact successor at line 438)

$ grep -n "0.1968\|0.0155\|0.1711\|0.2123" research/manuscripts/pinned-figures.json
   (no output — none of the four, nor the passing rho, is pinned today)

$ git ls-files | grep -i "PUB-ATR"
   (research/autonomy/hardening-state/PUB-ATR.json + 40 review-seat files;
    there is no research/manuscripts/PUB-ATR.json — my dispatch's path for it is wrong,
    and I did not write to either location)
```

**Closed items I confirm I am not replaying.** W17c's MDE range (`0.045–0.186`) — not re-derived, not recomputed, not mentioned as a result here. W17's Welch df-feasibility identity — not run. W17d's 90-slot point gate — not run. `p1s[2]` (the 22-vs-27 itemisation) — not attempted; it is prose and belongs to the manuscript owner. PUB-EMC-CLASSIFICATION — untouched (user-rejected, closed). No Brenca route touched. No network call of any kind was made.

---

## Method / inputs

Read-only reads of the live checkout at HEAD `d3e9c4d8`:

| File | What I took from it |
|---|---|
| `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` | lines 757–764 verbatim (`sed -n '757,764p'`) |
| `research/modalities/emc_atr_vulnerability.py` (186,461 B, mtime 2026-09-04) | `derive_part_d`, lines 2793–2960: the `< 15` power floor, the per-predictor `_per_drug` block that emits `{rho, t, n}`, `prolif_rho`, and the single line that consumes the `1.15` |
| `research/modalities/emc-atr-vulnerability.json` (342,797 B, mtime 2026-09-04) | every `n` under `part_d_drug_response_correlation`, plus `specificity[...]` for the passing, control, and replication-stress predictors |
| `research/manuscripts/lint_consistency.py` `check_artifact_figures` (l. 401–452) | how a pin resolves a key, and that a per-entry `scale` is applied **before** comparison |
| `research/manuscripts/pinned-figures.json` | confirmed none of the four is pinned |

Execution was entirely under `/tmp/claude-0/w17g/` (`enum_n.py`, `compute.py`, `run.txt`). Python 3 stdlib only (`json`, `math`, `collections`). No writes anywhere in the Git tree; no git write operation of any kind; `scripts/preflight.sh` not run (my dispatch did not ask for it).

---

## Result

### 1. The passage, verbatim, with line numbers `PRIMARY`

`research/manuscripts/dependency/emc-atr-vulnerability-assessment.md`, lines **757–764**:

```
757  ⚠ **No interval is computed anywhere in this analysis.** At n ≈ 700 the standard error on a single ρ is
758  ≈ 0.038, so **−0.164 and −0.171 are not distinguishable** and this row should be read as "does not beat
759  the proliferation control", **not** as "is beaten by it". The same applies to the **+0.157 / +0.173**
760  gap in the passing row. ⛔ **And it applies hardest to the test that PASSES.** Its "beats the proliferation control" bar is
761  `|ρ| > 1.15 × 0.1711` = **0.1968** (§1); +0.2123 clears it by **0.0155, 0.41× that standard error**,
762  comparing a CRISPR gene-effect score with an expression score over different line sets. **That test
763  passes on a margin this document cannot distinguish from zero.** ⚠ Its direction and its |ρ| ≥ 0.15
764  bar are untouched — both drugs clear 0.15 separately. **Nothing here rests on a
```

The four numbers under audit are all on **line 761**, except `≈ 0.038` and the phrase `n ≈ 700` which are on **757–758** and are pulled forward by the anaphor **"that standard error"** on line 761.

### 2. Which `n` values actually exist for that comparison `PRIMARY`

`derive_part_d` stores an `n` per (drug × predictor) pair inside `per_drug_rho_ATR_inhibitors`. The two ATR inhibitors are `azd6738` and `ve-822`. The relevant predictors:

| Predictor | azd6738 ρ (n) | ve-822 ρ (n) | mean ρ | role in the sentence |
|---|---|---|---|---|
| `dependency::ATR_ATRIP_CHEK1_mean_gene_effect` | **+0.252 (n=597)** | **+0.1726 (n=565)** | **+0.2123** | the **PASS row**; the `+0.2123` on line 761 |
| `expr::proliferation_MYC` | −0.0968 (n=**704**) | −0.2454 (n=**656**) | **−0.1711** | the specificity control; the `0.1711` on line 761 and the `−0.171` on line 758 |
| `expr::replication_stress` | −0.0879 (n=704) | −0.2394 (n=656) | **−0.1637** | the `−0.164` on line 758 |

`beats_the_proliferation_control` is `true` for the dependency predictor and `false` for replication stress, matching the prose. The artifact stores the **boolean and its two inputs, never the product** — confirming W17e: no field holds `0.1968`, `0.0155`, `0.038` or `0.41`.

The complete multiset of distinct `n` across every Part D (drug × predictor) cell:

```
ALL distinct n in part D correlations: [(565, 1), (595, 1), (596, 1), (597, 2), (601, 2),
                                        (656, 9), (702, 9), (704, 27), (711, 18)]
n_lines_with_residual per drug: {'azd6738': 956, 'bortezomib': 955, 'mk-1775': 965,
                                 'olaparib': 965, 'paclitaxel': 956, 'talazoparib': 954,
                                 've-822': 892}
```

**Every candidate reading of `n ≈ 700` enumerated from committed code and data** (16 candidates): the nine distinct correlation `n` (565, 595, 596, 597, 601, 656, 702, 704, 711); the two-value means 680 (704, 656) and 581 (597, 565); the pooled 1162 (597+565); the three distinct `n_lines_with_residual` (892, 956, 965); and 700 itself read as an exact stated approximation rather than a computed value.

### 3. Declared tolerance, and the expected-vs-observed table

**Tolerance declared before computing: exact agreement after rounding to the printed precision of each number** — bar `0.1968` → 4 dp; margin `0.0155` → 4 dp; SE `0.038` → 3 dp; ratio `0.41` → 2 dp. SE formula taken as the Fisher-z standard error `1/√(n−3)`, the form W17e used; `1/√(n−1)` and `1/√n` checked as alternates.

**The bar and the margin are `n`-independent and both survive, exactly:**

```
bar    = 1.15 × |−0.1711| = 0.196765 → 0.1968   printed 0.1968   MATCH
margin = 0.2123 − 0.1968  = 0.0155              printed 0.0155   MATCH
```

**The SE and the ratio, under every candidate `n`** (`PRIMARY` for every row; `margin = 0.0155`):

| `n` | SE = 1/√(n−3) | → 3 dp | SE ok? | margin/SE | → 2 dp | ratio ok? | Source of this `n` |
|---:|---:|---:|:--:|---:|---:|:--:|---|
| 704 | 0.037769 | 0.038 | ✅ | 0.41038 | 0.41 | ✅ | azd6738 `n` for `proliferation_MYC` **and** `replication_stress` — the −0.164 / −0.171 pair of line 758 |
| 702 | 0.037823 | 0.038 | ✅ | 0.40980 | 0.41 | ✅ | present in Part D correlations |
| 711 | 0.037582 | 0.038 | ✅ | 0.41243 | 0.41 | ✅ | largest `n` anywhere in Part D correlations |
| 700 | 0.037878 | 0.038 | ✅ | 0.40921 | 0.41 | ✅ | the literal printed `n ≈ 700` taken as an exact stated approximation |
| 680 | 0.038433 | 0.038 | ✅ | 0.40330 | **0.40** | ❌ | mean of the two expression `n` (704, 656) |
| 656 | 0.039133 | **0.039** | ❌ | 0.39608 | **0.40** | ❌ | ve-822 `n` for the same two expression predictors |
| 601 | 0.040893 | **0.041** | ❌ | 0.37904 | **0.38** | ❌ | present in Part D correlations |
| **597** | **0.041030** | **0.041** | ❌ | **0.37777** | **0.38** | ❌ | **azd6738 `n` for the dependency predictor — the PASS row** |
| 596 | 0.041065 | 0.041 | ❌ | 0.37745 | 0.38 | ❌ | present in Part D correlations |
| 595 | 0.041100 | 0.041 | ❌ | 0.37713 | 0.38 | ❌ | present in Part D correlations |
| **565** | **0.042182** | **0.042** | ❌ | **0.36745** | **0.37** | ❌ | **ve-822 `n` for the dependency predictor — the PASS row** |
| 581 | 0.041595 | 0.042 | ❌ | 0.37265 | 0.37 | ❌ | mean of the two dependency `n` (597, 565) |
| 892 | 0.033539 | 0.034 | ❌ | 0.46215 | 0.46 | ❌ | `n_lines_with_residual`, ve-822 |
| 956 | 0.032393 | 0.032 | ❌ | 0.47850 | 0.48 | ❌ | `n_lines_with_residual`, azd6738 |
| 965 | 0.032241 | 0.032 | ❌ | 0.48075 | 0.48 | ❌ | largest `n_lines_with_residual` |
| 1162 | 0.029374 | 0.029 | ❌ | 0.52768 | 0.53 | ❌ | 597 + 565 pooled |

Inverse solve (all integer `n` in 4…2999): SE rounds to `0.038` for **n ∈ [678, 714]**; the ratio rounds to `0.41` for **n ∈ [686, 719]**; the intersection reproducing **both** printed numbers is **n ∈ [686, 714]**. Under `1/√(n−1)` and `1/√n` the picture is unchanged in kind — 704, 702, 711 and 700 match, 680 and 656 fail the ratio, and no dependency-row `n` matches under any of the three formulas.

**Answer to "which `n` is the SE meant to use".** The SE was computed from an `n` in **[686, 714]**, and the only committed value in that window that is a real `n` for the predictors *named in the preceding sentence* is **704** — the azd6738 `n` shared by `expr::proliferation_MYC` and `expr::replication_stress`. So line 757–758's `n ≈ 700` is honest **for the sentence it sits in** (the −0.164 vs −0.171 expression pair, n = 704 and 656). What fails is line 761's re-use of it: **"that standard error" is transported onto the dependency row, whose own `n` are 597 and 565, and neither reproduces `0.038` or `0.41` under any of the three SE formulas.**

### 4. What the correct numbers are for the row line 761 is actually about `PRIMARY`

| Reading | SE | margin in SE |
|---|---:|---:|
| printed on line 761 (borrowed from n≈700) | 0.038 | **0.41×** |
| at the PASS row's larger `n` = 597 (azd6738) | 0.041 | **0.38×** |
| at the PASS row's smaller `n` = 565 (ve-822) | 0.042 | **0.37×** |

**The error runs in the conservative direction.** Using the dependency row's own `n` makes the SE *larger* and the clearance *smaller* — 0.37–0.38 SE rather than 0.41 SE. The document's actual claim at line 763, *"That test passes on a margin this document cannot distinguish from zero"*, is therefore **not weakened by the defect; it is slightly understated.** No conclusion in §5.1 flips. This is a precision-and-provenance defect, not a claim-reversing one.

**A further caveat I observed but am not repairing** (flagging only, for the owner): `0.0155` is a difference between a correlation from the **dependency** predictor (n = 597/565) and one from the **expression** control (n = 704/656) — different instruments, different line sets, which line 762 already says. The standard error of *that difference* is not a single-ρ SE at any `n`; it is at least √2 larger if the two were independent, and the two are not independent. So "0.41× that standard error" understates the imprecision by more than the `n` substitution alone accounts for. Quantifying it needs a covariance the artifact does not carry, so I make no number claim about it — **UNKNOWN**.

### 5. The unsigned `0.1711` question — settled: **neither** `PRIMARY`

W17e flagged that §5.1 prints `0.1711` unsigned against `part_d_drug_response_correlation.specificity."expr::proliferation_MYC".mean_rho_across_ATR_inhibitors`, whose value is **−0.1711**, and correctly moved that pin to the §5 table header (which prints `−0.171`) after it failed as `A-figure-mismatch`.

**It is neither a prose defect nor an artifact naming defect.**

- **Not a prose defect.** Line 761 prints the magnitude *inside an absolute-value expression*: `|ρ| > 1.15 × 0.1711`. That is exactly what the code computes — `abs(rho) > abs(prolif_rho) * 1.15` at `emc_atr_vulnerability.py:2935`. Writing the signed `−0.1711` there would make the inequality **wrong**, since `1.15 × −0.1711` is negative and every `|ρ|` exceeds it. The prose is right.
- **Not an artifact naming defect.** `mean_rho_across_ATR_inhibitors` is a signed mean of signed Spearman ρ, correctly named and correctly signed; the sign carries the direction of the association and must be retained.

What actually failed was the **pin**, not either artifact. `lint_consistency.check_artifact_figures` (l. 425) applies a per-entry `scale` **before** comparison, for precisely this class of unit/representation mismatch. A second pin on the same key with `"scale": -1.0` yields `+0.1711` and gates line 761's magnitude form directly, with the existing signed pin still gating the §5 table header. No file needs to change for this — only the pin registry entry, which is part of the routed repair below and which I have **not authored**.

---

## Smallest correct repair — ROUTED, NOT AUTHORED

Routed to the **manuscript owner of PUB-ATR** as one item. **I did not edit the manuscript, `research/modalities/emc_atr_vulnerability.py`, `research/manuscripts/pinned-figures.json`, `research/autonomy/hardening-state/PUB-ATR.json`, or any review-seat file, and I did not open a review round.** The description below is a routing note, not a patch.

The repair has two halves, and the first is **mandatory on correctness grounds** while the second is what makes `--check` able to hold it:

**(a) Prose — required, because the printed value is wrong for the row it describes.** Line 761's `0.41× that standard error` transports an SE computed at the expression predictors' `n` onto the dependency row. The smallest correct prose change names the `n` the ratio uses. Two defensible forms, the owner's choice: state the ratio at the PASS row's own smaller `n` = 565 (**0.042 SE, 0.37×**, the conservative reading, consistent with the paragraph's argument); or give the range **0.37–0.38×** across the row's two `n` (565 and 597) and say so. Either way line 757's `n ≈ 700` should be qualified as belonging to the *expression* comparison it introduces, so line 761 stops inheriting it silently. The document's conclusion does not change — it becomes marginally stronger.

**(b) Artifact — required for `--check` to re-derive any of the four.** The specificity block already carries `mean_rho_across_ATR_inhibitors`, `proliferation_control_rho`, `beats_the_proliferation_control` and the per-drug `{rho, t, n}`. It does not carry the product, the difference, or any `n` summary for the predictor. Adding, per specificity record where `beats_the_proliferation_control` is not `None`, four derived fields — the multiplier `1.15` (today a bare literal at `:2935`), the bar `|prolif_rho| × 1.15`, the margin `|rho| − bar`, and the row's own minimum `n` across its ATR inhibitors — makes all four printed numbers re-derivable offline, and lets `pinned-figures.json` gate them with four `artifact_figures` entries plus the `scale: -1.0` entry from §5 above. Note that the fifth quantity (the SE and the ratio) follows from the minimum `n` alone; whether to emit it as a field or compute it in the pin's `scale` is the owner's call.

**Ordering matters:** (b) implemented honestly will emit `0.37×`/`0.042`, so it will *fail* against the current prose. (a) must land first or with it.

---

## Validation evidence

**RUN.** Environment: `/tmp/claude-0/w17g/`, `python3` stdlib only, no network, HEAD `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`, tree clean.

Script 1 — `/tmp/claude-0/w17g/enum_n.py` (enumerates every `n` in Part D from the committed artifact). Verbatim key output already quoted in Result §2; the per-drug blocks it printed:

```
== dependency::ATR_ATRIP_CHEK1_mean_gene_effect
  mean_rho_across_ATR_inhibitors: 0.2123
  proliferation_control_rho: -0.1711
  beats_the_proliferation_control: True
  per_drug_rho_ATR_inhibitors: {
  "azd6738": { "rho": 0.252,  "t": 6.352, "n": 597 },
  "ve-822":  { "rho": 0.1726, "t": 4.157, "n": 565 } }

== expr::proliferation_MYC
  mean_rho_across_ATR_inhibitors: -0.1711
  beats_the_proliferation_control: None
  per_drug_rho_ATR_inhibitors: {
  "azd6738": { "rho": -0.0968, "t": -2.578, "n": 704 },
  "ve-822":  { "rho": -0.2454, "t": -6.473, "n": 656 } }
```

Script 2 — `/tmp/claude-0/w17g/compute.py` (the full expected-vs-observed table). Final run:

```
$ cd /tmp/claude-0/w17g && python3 compute.py > run.txt 2>&1; echo "EXIT=$?"; wc -l run.txt
EXIT=0
43 run.txt
```

Verbatim tail of `run.txt`:

```
Inverse solve: which n give SE rounding to 0.038 (Fisher 1/sqrt(n-3))?
  n range: 678 .. 714
Inverse solve: which n give ratio rounding to 0.41?
  n range: 686 .. 719
Intersection: [686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700,
               701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714]
```

**Honest failure preserved.** The first execution of `compute.py` exited **1** with `ValueError: math domain error` — my inverse-solve loop started at `n=2`, so `sqrt(n-3)` was called on a negative argument. I corrected the loop bound to `range(4, 3000)` and re-ran to exit 0. The table rows above the inverse solve were already printed and identical in both runs; nothing was weakened to make anything pass.

**PROPOSED (NOT RUN).** The four `artifact_figures` entries and the `scale: -1.0` entry described in the repair — not authored, not written, not linted, and `research/manuscripts/lint_consistency.py` was **not** executed against any proposed pin. `scripts/preflight.sh` was **not** run. `emc_atr_vulnerability.py --check` was **not** run.

---

## Limitations

- **No clinical claim.** Nothing here establishes EMC ATR-pathway biology, efficacy, safety, selectivity, therapeutic window or clinical readiness. Every number is a Spearman correlation over cell-line panels; this is `PREDICTION`/association at best and here it is purely an arithmetic audit of printed values.
- **The SE formula is an inference, not a recorded choice.** The document does not state which SE it used. I tested `1/√(n−3)`, `1/√(n−1)` and `1/√n`; all three give the same verdict (no dependency-row `n` matches, 704/702/711/700 do). The authors' actual formula and their actual `n` remain **UNKNOWN** — I recovered only the interval `n ∈ [686, 714]` that reproduces both printed numbers.
- **`n ≈ 700` may have been intended as a stated approximation** rather than a computed value; 700 itself reproduces both numbers. In that reading line 757 is not defective at all and only line 761's inheritance of it is. I cannot distinguish the two readings from committed evidence.
- **The SE of the difference is not quantified.** The margin compares two correlations from different instruments over different line sets; the proper SE of that difference needs a covariance the artifact does not carry. **UNKNOWN**, and the 0.37–0.38× figure is therefore itself an upper bound on the clearance.
- **HEAD divergence.** I read `d3e9c4d8`, not the `92abbcb9` named in `COMMON-BRIEF.md`. The two input files (`emc_atr_vulnerability.py`, `emc-atr-vulnerability.json`) both carry mtime 2026-09-04 and the tree is clean, but I did not diff them against `92abbcb9` and cannot assert they are identical there.
- I did not consult the frozen corpus; my novelty claim is scoped to lane 17's transferred reports plus the `rg`/`git ls-files` searches quoted above, and to nothing wider.

---

## Stop condition

**Set:** the passage quoted with its line; every candidate `n` enumerated from committed code and data; all four numbers computed under each with a tolerance declared before computing and a real exit code; the smallest correct repair routed unauthored.

**Met, in full.** Passage quoted (lines 757–764, the four numbers on 761 and 757–758). Sixteen candidate `n` enumerated from `derive_part_d` and the artifact, plus an exhaustive integer inverse solve. Tolerance declared before the first computation (printed precision per number) and all four computed under every candidate; exit code 0 on the final run, with the earlier exit-1 failure preserved above. Repair routed to the manuscript owner in two ordered halves, authored into no file. The secondary unsigned-`0.1711` question is settled as **neither** defect, with the mechanism (`scale`) that resolves it named.

The dispatch's alternative branch — "if no candidate `n` reproduces all four, that is a finding" — did **not** trigger: four candidates reproduce all four numbers. The finding is the sharper one: the `n` that reproduces them is **not the `n` of the row the sentence is about**.

---

## Tool-call and wall-clock count actually used

**14 tool calls** (all Bash; no Read/Edit/Write, no network, no MCP). **Wall clock 02:38:45Z → 02:40:29Z ≈ 1 min 44 s of timed execution**, plus report drafting. Well inside the ~40-call / ~40-minute self-observed target.

---

## Next concrete action

**One successor, inside lane 17:** verify the repair once the manuscript owner lands half (a), by running `python3 research/modalities/emc_atr_vulnerability.py --check` and `lint_consistency.py` against the proposed `artifact_figures` entries and confirming the four §5.1 numbers gate cleanly at the PASS row's own `n` — the first end-to-end `--check` evidence that §5.1's clearance cluster is re-derivable rather than prose-only. This is blocked until the owner acts; it is not work this lane can do read-only.

If that stays blocked, the honest alternative is: **no further viable successor on §5.1 in this lane**, because W17e's audit found 0 confirmed prose-vs-artifact disagreements outside the retained appendix and this report closes the last prose-only quantitative claim it isolated. The remaining known item, `p1s[2]`, is explicitly the manuscript owner's prose call and out of lane.
