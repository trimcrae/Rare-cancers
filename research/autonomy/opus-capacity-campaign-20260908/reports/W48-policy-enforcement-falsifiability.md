<!-- collected 2026-09-08T04:45:25Z by campaign coordinator; agent id a24db27cf8b32b54c; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a24db27cf8b32b54c.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted. Report follows.

## Worker

**W48**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: evidence-contract enforcement — executable falsifiability of the POLICY-evidence gates.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in my environment corroborates it — no variable names a model. The coordinator must extract the served model from the transcript.

Start `date -u`: `Tue Sep  8 04:39:55 UTC 2026`. End `date -u`: `Tue Sep  8 04:42:15 UTC 2026`.
Start HEAD: `408b676aec3625a36917755662516232a27a1278`, `git status --porcelain` empty.
End HEAD: `7a1002679e0830fb19bed48660772cdcc91c495d`, `git status --porcelain` empty. HEAD moved under me (coordinator collection). Verified the four files I measured are byte-identical across the move: `git diff --stat 408b676a HEAD -- systems/POLICY-evidence.md scripts/validate-registry.mjs research/data/emc-clinical-registry.json systems/systems_check.py` → **empty output, exit 0**. Nothing I measured changed.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start of run, complete):

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...(same list as no_proxy)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy/truststore flags only)
NO_PROXY=(same list as no_proxy)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=(same list as no_proxy)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

No variable in that set names a model. (Re-run at end of session: identical.)

## Question

**As dispatched:** for each of the 16 numbered requirement units in `systems/POLICY-evidence.md`, which executable gate enforces it, and can that gate actually fail on a violation?

**As actually pursued, after the mandatory prior-work check:** the *static* half of that question is already closed by **W30c** (`reports/W30c-policy-sections-without-gates.md`, §5.2, titled "The enforcement map — all 16 units"). Re-deriving it would be exactly the replay `CLAUDE.md` §5 forbids. I pivoted to the half W30c explicitly did **not** do:

> **Can each gate actually fail? Measured by execution, not by reading the source.**

W30c's map is entirely source-read — it ran no mutation, and its own Validation-evidence section runs only greps and read-only registry enumeration. Its classifications "enforced", "gate weaker than the text", "enforced vacuously" are therefore *predictions about program behaviour*, not observations of it. Two of them turn out to be wrong. I also examined `systems/systems_check.py` as a candidate enforcer, which W30c never did.

## Prior-work check

```
$ ls research/autonomy/opus-capacity-campaign-20260908/reports/ | grep -iE 'W30|W48'
W30-registry-policy-conformance.md
W30b-policy-2.6-2.7-conformance.md
W30c-policy-sections-without-gates.md          # ← W30d has NOT landed; W30c is the sibling that matters
```

I read `W30c-policy-sections-without-gates.md` §5.2–§5.7 in full. **My dispatched question is already answered there statically.** I am not re-deriving its table; I cite it and test it. The dispatch named "W30d"; no `W30d-*` file exists at either HEAD — that is UNKNOWN (not yet collected), not absent.

```
$ grep -rn "validate-registry" --include='*.sh' --include='*.yml' --include='*.py' --include='*.md' . | grep -v opus-capacity-campaign
   → 19 hits across README.md, systems/MIGRATION.md, systems/POLICY-evidence.md, systems/systems_check.py:1555,1753,
     research/hypotheses/METHODOLOGY.md, 4 manuscripts, 2 sprint records. No test module.

$ grep -n -iE "POLICY-evidence|emc-clinical-registry|evidenceQuestions|registry\.citations|wilson|studyPeriod|populationKey" systems/systems_check.py
   1528, 1555, 1753, 1754   (four hits, all inside check [P1])
```

Closed items I confirm I am not replaying: the registry ICD-O classification paper (user-rejected), the §2.6/§2.7 conformance audit (W30b), the campaign resolution rate (W36/W36b), the `origin/literature-cache` question (W40). I did not read or reference any `reports/W25-*`.

## Method and inputs

- Read in full: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `systems/POLICY-evidence.md` (386 lines), `scripts/validate-registry.mjs` (170 lines), `reports/W30c-policy-sections-without-gates.md` §Result.
- Read targeted: `systems/systems_check.py:1520–1570, 1740–1765`.
- **Mutation harness.** Because `validate-registry.mjs` resolves its input as `dirname(import.meta.url)/../research/data/emc-clinical-registry.json` (`:23–24`), I built a sandbox **outside the repository** at `/tmp/claude-0/w48/sbx/` containing a copy of the script and a copy of the registry, and mutated only the copy. The repository registry was never opened for writing; `git status --porcelain` is empty at start and end.
- Driver: `python3` (stdlib only) applying one deliberate policy violation per run to a deep copy of the registry, invoking `node scripts/validate-registry.mjs`, and recording exit code plus ERROR/WARN lines. **41 mutations** + 5 dedup probes + 1 baseline.
- `node v22.22.2`, `python3` system interpreter, `git`. No network, no pytest run, no preflight, no GPU, no paid API.

**Enumeration of the 16 units** (numbered requirement units in the file; note §4 contains two sections numbered 4.3, which W30c also records): 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3, 4.1, 4.2, 4.3-bias, 4.3-generalization, 5.

## Result

### R-1. Candidate enforcers, measured

| Enforcer | Enforces a POLICY-evidence requirement unit? | Evidence |
|---|---|---|
| `scripts/validate-registry.mjs` | **Yes** — the only commit-loop enforcer of any unit | 170 lines, mutation-tested below | PRIMARY |
| `systems/systems_check.py` | **No.** Its only four references are inside check `[P1]` (`:1528` `GATE_ORDINAL_DOCS`, `:1555` `_GATE_TOOLS`, `:1753–1754`), which checks that *documents naming the validator state the right preflight gate ordinal*. That is a documentation-consistency check about the enforcer's **position in preflight**, not about any of the 16 units. | grep, 4 hits, source read | PRIMARY |
| Any test of `validate-registry.mjs` | **None exists.** `grep -rn "validate-registry" --include='test_*.py'` → 0 modules (W30c's finding, re-confirmed by my grep across `*.sh|*.yml|*.py|*.md`). | PRIMARY |
| Modality/manuscript pytest modules | Cover §2.1(3), §2.2, §2.4, §2.6, §2.7 — but all in **opt-in** tiers (W30c §5.2, not re-measured by me). **I ran none of them and assert no pass or fail.** | SECONDARY (W30c) |

So the falsifiability question reduces to: **what can gate 10 actually fail on?** That is what I measured.

### R-2. The executed falsifiability map — 16 units

Classification is by the dispatch's scheme, decided by **execution against the live registry shape**. `E-AND-F` = ENFORCED-AND-FALSIFIABLE (a run exited 1); `WARN-ONLY` = a check exists and prints, but **cannot fail a gate** — preflight stays green; `E-VAC` = a check exists but cannot fail on current data shapes; `UNENF` = no check at all. All rows PRIMARY (I ran them).

| § | Testable predicate | Enforcer (file:line) | Mutation actually run | Observed | Class |
|---|---|---|---|---|---|
| **1.1** | every patient/cohort/position/systemicEvidence row's `sourceId` resolves in `registry.citations` | `validate-registry.mjs:73, :85, :133, :149` | dangling `sourceId` at each of the 4 sites | **exit 1** at all four | **E-AND-F** |
| **1.2** | citation has `title`, `year`, ≥1 of pmid\|pmcid\|doi, `url` | `:55, :56, :57, :58` | delete each in turn | **exit 1** ×4 | **E-AND-F** |
| **1.2** | `license` is recorded | `:59` (`warns.push`) | delete `license` | exit **0**, 1 WARN | **WARN-ONLY** |
| **1.2/1.3** | `verified:true` only when the link was opened and confirmed | — | flipped **all 25** `verified` to `false` | exit 0, silent | **UNENF** (no code reads the field) |
| **1.3** | `provenance:"secondary"` ⇒ `primaryRef` present | `:86–87` (cohorts), `:134` (positions), `:150` (systemicEvidence) | drop `primaryRef` on a secondary cohort; on a secondary position | **exit 1** both | **E-AND-F** |
| **1.3** | never invent an identifier for an unfetched primary | — | replaced a real DOI with `10.9999/this-doi-does-not-exist` | exit 0, silent | **UNENF** (no identifier is ever resolved) |
| **2.1(1)** | confirmed EMC, matching the page | — | appended a pooled cohort labelled *"Osteosarcoma cohort, not EMC"* | exit 0, silent | **UNENF** |
| **2.1(2)** | explicit **integer** `{events, denom}`, never back-derived from a percentage | `:96–99` | `events = 3.5` | **exit 0, silent** | **E-VAC for integer-ness** — the test is `typeof !== "number"`, and `3.5` is a number. Confirms W30c's F2-1 by execution. |
| **2.1(2)** | events ≤ denom | `:98` | `events = denom+1` | **exit 1** | **E-AND-F** |
| **2.1(2)** | a pooled cohort must *have* counts | `:96` (`if (m && …)`) | deleted all four metric blocks from a pooled cohort | exit 0, silent | **UNENF** (presence never required) |
| **2.1(3)** | outcome ≠ inclusion criterion | not in the validator; in `meta-analysis.mjs:36`, run by no gate | set a pooled cohort `stage:"distant"` with `metastasis = n/n` | exit 0, silent | **UNENF at gate 10** |
| **2.2** | denominator-weighted pool; **Wilson** interval; heterogeneity as range | — | added `pooledSummary:{method:"normal approximation", I2:0.9, ci:[…]}` | exit 0, silent | **UNENF** |
| **2.3** | within-study: pooled strata disjoint | `:113–117` (`warns.push`) | duplicate a pooled cohort | **see R-3 — silent for cohort[0], WARN for 1–4** | **WARN-ONLY, and partly E-VAC (new defect)** |
| **2.3** | across studies: overlapping series `pool:false` + `contextReason` | `:88` (`warns.push`, and only for the `pool:false` direction) | flipped an overlap-flagged cohort to `pool:true` and dropped its reason | exit 0, **silent** — no warning at all | **UNENF for the across-study direction** |
| **2.3** | a `pool:false` cohort states a `contextReason` | `:88` | dropped `contextReason` from a context cohort | exit 0, 1 WARN | **WARN-ONLY** |
| **2.4** | time-anchored survival never merged | — | added `pooledFiveYearDSS:{mergedFrom:[…]}` | exit 0, silent | **UNENF** (W30c called it "enforced vacuously"; there is no check to be vacuous — nothing reads these fields) |
| **2.5** | stated limitations shown | — (the named surface is the retired site) | deleted every `limitation`/`caveat` key | exit 0, silent | **UNENF** |
| **2.5-adjacent** | non-real data must be bannered | `:48–49` | `dataStatus:"SAMPLE_SYNTHETIC"` + no `dataStatusBanner` | **exit 1** | **E-AND-F** (but see R-4: banner is not required for `partial-curated`) |
| **2.6** | study-level descriptive series (a)–(h): no cross-population pool, no I², no inverse-variance weighting | — | added `descriptiveSeries` with `pooledProportion`, `ci95`, `I2`, `weighting:"inverse-variance"` — four §2.6(c) prohibitions at once | exit 0, silent | **UNENF** |
| **2.7** | reconstructed IPD: risk table mandatory, digitization provenance required, labelled as a reconstruction | — | added `reconstructedIPD` with `riskTable:null`, `digitizedBy:null`, `labelledAsReconstruction:false` | exit 0, silent | **UNENF** |
| **3** | `contested` ⇒ ≥2 opposing positions | `:137–141` | two `supports`, no `against` | **exit 1** | **E-AND-F** |
| **3** | …but *"≥2 positions"* as written | `:139` | **one single `mixed` position** | **exit 0, silent** | **E-VAC for the "≥2" clause** — confirms W30c's F2-2 by execution |
| **3** | at least one position exists | `:129` | zero positions | **exit 1** (2 errors) | **E-AND-F** |
| **3** | name the mechanism of conflict (`caveat`); `bottomLine` states what is unproven | — | stripped every `caveat`; stripped every `bottomLine` | exit 0, silent (both) | **UNENF** |
| **4.1** | `studyPeriod` is `[start,end]`, start≤end≤CUR+1 | `checkPeriod :63–68` | reversed `[2022,2002]`; future `[2002,2099]` | **exit 1** both | **E-AND-F** |
| **4.1** | a pooled cohort carries `studyPeriod` or `studyPeriodUnknown` | `:90–91` (`warns.push`) | deleted both | exit 0, 1 WARN | **WARN-ONLY** |
| **4.1** | record it **only from what the source states**; never infer | — | substituted a well-formed but unsupported `[1990,2001]` | exit 0, silent | **UNENF** (shape is checkable, provenance is not) |
| **4.2** | vintage surfaced everywhere; "diagnosed since" control | — (retired site surface) | removed `studyPeriod` from **all** 25 citations and all 14 cohorts | exit 0, silent | **UNENF** |
| **4.3-bias** | never silently adjust a number upward | — | added `eraAdjustment:{multiplier:1.35, applied:true}` | exit 0, silent | **UNENF** |
| **4.3-gen** | any pooled figure travels with its vintage | — | pooled cohort with `fiveYearDSS` and no `studyPeriod` | exit 0, silent | **UNENF** |
| **5** | the checklist | derivative of §1–§4 + "run the validator" | — | inherits every row above | **derivative** |

### R-3. NEW FINDING — a falsy-index bug makes §2.3's double-counting guard blind to the first pooled cohort

`validate-registry.mjs:113–116`:

```js
if (c.pool !== false && c.populationKey) {
  const key = `${c.populationKey}::${c.stratum || ""}`;
  if (poolKeys[key]) warns.push(`${cw} shares populationKey+stratum with cohort[${poolKeys[key]}] …`);
  else poolKeys[key] = i;
}
```

`poolKeys[key] = i` stores the **array index**, and index `0` is falsy in JavaScript. So the first pooled cohort's key is written and then, on any later collision, `if (poolKeys[key])` evaluates `0` → falsy → **no warning, and the map entry is silently overwritten with the duplicate's index**. Measured by duplicating each pooled cohort in turn:

```
dup of cohort[0] popKey='masunaga2025-jpreg' stratum='localized-surgical' rc=0 dedup-warn=NO
dup of cohort[1] popKey='masunaga2025-jpreg' stratum='metastatic-at-dx'  rc=0 dedup-warn=YES
dup of cohort[2] popKey='meisKindblom1999'   stratum=None                rc=0 dedup-warn=YES
dup of cohort[3] popKey='ussc2022'           stratum=None                rc=0 dedup-warn=YES
dup of cohort[4] popKey='chiusole2020'       stratum=None                rc=0 dedup-warn=YES
```

**1 of 5 pooled cohorts is unprotected**, and it is the largest one — `masunaga2025-jpreg / localized-surgical`, the Japanese national registry stratum the policy itself flags as dominating the pool (§2.2 "currently a single national registry does"). Duplicating precisely that cohort is the *cardinal sin* §2.3 names, and it produces a **completely silent** run. W30c classified this row as "DEFAULT (advisory) — gate weaker than text"; the measured state is weaker still: for cohort index 0 there is no signal at all. I am reporting the diagnosis only — **per my dispatch I have authored no patch, no test and no repair, and I propose none here.**

This is a **latent** defect: the live registry has 0 collisions today (W30c C-6, which I did not re-derive), so nothing is currently mis-pooled. It bounds what the guard *could* catch, not what it has missed.

### R-4. Second correction to W30c, measured

W30c's table row for §2.5 and the file's `dataStatusBanner` rule: the banner ERROR at `:48–49` fires **only** when `dataStatus === "SAMPLE_SYNTHETIC"`. The live registry is `partial-curated`, so **deleting `dataStatusBanner` outright is a silent pass** (measured, exit 0). The check is E-AND-F for its own stated trigger and E-VAC for the current data shape — it cannot fire on this registry without also changing `dataStatus`. `systems/MIGRATION.md:475` already records the adjacent fact that the banner is checked "for presence, not content"; the status-conditionality is the further step.

### R-5. Counts

Denominator = **31 decidable predicates** extracted from the 16 units (a unit with several independent obligations contributes several rows; §5 is derivative and excluded from the count).

| Class | n | Share |
|---|---|---|
| **ENFORCED-AND-FALSIFIABLE** (a run exited 1) | **11** | 35% |
| **WARN-ONLY** (check exists, prints, cannot fail the gate) | **4** | 13% |
| **ENFORCED-VACUOUSLY** (check exists, cannot fail on current data shapes) | **3** | 10% |
| **UNENFORCED** (no check anywhere in the commit loop) | **13** | 42% |

At the level of the **16 units**: 5 units have at least one E-AND-F predicate (**1.1, 1.2, 1.3, 3, 4.1**), 1 unit is mixed E-AND-F/E-VAC/UNENF (**2.1**), 1 is WARN-ONLY+E-VAC (**2.3**), 1 has an E-AND-F check adjacent to but not identical with its text (**2.5**), **6 units have no executable enforcement at any tier reachable by a bare commit** (**2.2, 2.4, 2.5-as-written, 2.6, 2.7, 4.2, 4.3-bias, 4.3-gen** — 8 sub-units across 6 numbered slots), and **5** is derivative.

The three E-VAC rows are: §2.1(2) integer-ness (`3.5` is a `number`), §3's "≥2 positions" (one `mixed` satisfies the disjunct), and §2.3's guard for cohort index 0 (R-3). Two of those three were *predicted* by W30c from source; the third was not, and would not have been found without running the code.

## Validation evidence

**RUN.** Environment: `/home/user/Rare-cancers` (read-only for me), HEAD `408b676a` → `7a100267`; execution in `/tmp/claude-0/w48/sbx/` (since deleted); `node v22.22.2`; system `python3`, stdlib only.

Baseline, unmutated copy of the live registry:
```
$ cd /tmp/claude-0/w48/sbx && node scripts/validate-registry.mjs
OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).
BASELINE_EXIT=0
```

41-mutation sweep, verbatim excerpt (full table in R-2; `e=`/`w=` are ERROR/WARN line counts):
```
1.1a patients[0].sourceId -> dangling                      FAILS(exit1) e=1 w=0
1.2e delete license                                        WARN-ONLY    e=0 w=1
1.2f flip every verified -> false                          SILENT-PASS  e=0 w=0
1.3c invent a bogus unresolvable DOI on a citation          SILENT-PASS  e=0 w=0
2.1(1) add pooled cohort of a DIFFERENT cancer (not EMC)   SILENT-PASS  e=0 w=0
2.1(2)i events=3.5 (back-derived from a percentage)        SILENT-PASS  e=0 w=0
2.1(2)ii events > denom                                    FAILS(exit1) e=1 w=0
2.1(3) pooled cohort whose inclusion criterion IS the outcome  SILENT-PASS e=0 w=0
2.2 add pooledSummary claiming a normal-approx CI          SILENT-PASS  e=0 w=0
2.3a two pooled cohorts share populationKey+stratum        SILENT-PASS  e=0 w=0
2.3b overlapping cohort flipped to pool:true, no reason    SILENT-PASS  e=0 w=0
2.4 merge two cohorts' 5-yr DSS into one pooled field      SILENT-PASS  e=0 w=0
2.5a drop dataStatusBanner (status partial-curated)        SILENT-PASS  e=0 w=0
2.5b dataStatus=SAMPLE_SYNTHETIC with no banner            FAILS(exit1) e=1 w=0
2.6 cross-population pooled proportion + CI + I2           SILENT-PASS  e=0 w=0
2.7 reconstructed IPD, no risk table, no provenance        SILENT-PASS  e=0 w=0
3a contested with only ONE 'mixed' position                SILENT-PASS  e=0 w=0
3b contested with two 'supports' and no 'against'          FAILS(exit1) e=1 w=0
3c every position loses its caveat                         SILENT-PASS  e=0 w=0
4.1a studyPeriod reversed [2022,2002]                      FAILS(exit1) e=1 w=0
4.1c pooled cohort loses studyPeriod entirely              WARN-ONLY    e=0 w=1
4.1d fabricated studyPeriod (well-formed, unsupported)     SILENT-PASS  e=0 w=0
4.3(i) silently adjust a pooled rate upward (×1.35)        SILENT-PASS  e=0 w=0
DRIVER_EXIT=0
```

Dedup probe output is quoted verbatim in R-3.

Write-isolation evidence:
```
$ git status --porcelain                      # start:  (empty)
$ git status --porcelain                      # end:    (empty)
$ git diff --stat 408b676a HEAD -- systems/POLICY-evidence.md scripts/validate-registry.mjs \
      research/data/emc-clinical-registry.json systems/systems_check.py
(empty)  diff-exit=0
$ rm -rf /tmp/claude-0/w48                    # scratch deleted; /tmp/claude-0/w48 no longer listed
```

**PROPOSED (NOT RUN).** Every pytest module W30c names as covering §2.1(3), §2.2, §2.4, §2.6, §2.7. I ran **none** of them and assert no pass or fail for any. (The brief records that `pytest` 9.1.1 *is* installed at `/root/.local/bin/pytest` and that W30c's "`No module named pytest`" line measured the wrong interpreter — I did not exploit that, because a pytest tier is outside my bounded question and running `test_endpoint_producers_check.py` perturbs committed artifacts.) I did not run `scripts/preflight.sh`, `meta-analysis.mjs`, `systems_check.py`, or any generator.

## Limitations

- **The 31-predicate denominator is my decomposition**, not the file's. §2.6 alone has eight lettered obligations that I collapsed into one row because one mutation violates four of them simultaneously; a finer split would raise the UNENFORCED share, not lower it.
- **A SILENT-PASS proves the gate is blind to *that* mutation**, not that no enforcement exists anywhere. Five units are covered by opt-in pytest tiers I did not run; my UNENFORCED label is scoped to "no check reachable by a bare commit-time run of gate 10", and R-1 states that scope.
- **Mutations are synthetic**. Injecting `descriptiveSeries` or `reconstructedIPD` keys tests whether the validator *would* police such a structure; it does not establish that any real artifact uses those key names. The §2.6/§2.7 artifacts live in `research/modalities/`, not the registry.
- Every finding is about **repository tooling**. Nothing here is a clinical claim: no statement about radiotherapy, chemotherapy, any agent's efficacy, safety, selectivity or therapeutic window, and no patient-level inference. The registry's actual conformance is 0 violations (W30c §5.3) and I did not re-derive it.
- R-3 and R-4 are **latent** defects with a measured live exploitation count of **zero**. They bound what the guard can catch; they are not evidence that anything in the tree is currently mis-pooled.
- I authored no repair, no patch, no gate and no test, and I weakened nothing.

## Stop condition

**Set up front:** return as soon as every one of the 16 units has been classified by an *executed* mutation against the real enforcer, with exit codes recorded, plus a determination of whether `systems_check.py` enforces any unit.

**Met.** 41 mutations + 5 dedup probes executed, all 16 units classified, `systems_check.py` determined to enforce none of them (only the `[P1]` gate-ordinal documentation check), and two of W30c's source-read classifications corrected by measurement.

## Tool-call and wall-clock count actually used

**11 tool calls. ~2.3 minutes wall clock** (`04:39:55Z` → `04:42:15Z`). Well inside the ~40/~40 target; returning early rather than padding.

## Next concrete action

**One specific successor, for whoever owns `scripts/validate-registry.mjs`** (not me — I am read-only and forbidden to author it): the smallest correct repair for R-3 is to make the dedup map's occupancy test explicit rather than truthiness-based at `validate-registry.mjs:115`, and the honest way to land it is with a mutation test that duplicates **cohort index 0** specifically — the case that currently passes silently — since a test that duplicates any other index would have passed before the fix too. That routing note is the artifact; the diff is the owner's to write.

A second, independent successor for this lane: **§2.3's across-study direction has no check in either direction I could find** — flipping an `overlap`-flagged cohort to `pool:true` and deleting its `contextReason` produced neither an error nor a warning (measured, R-2). W30c recorded "Across studies: nothing" from source; it is now confirmed by execution. Whether the opt-in modality tests cover it is **UNKNOWN** — I ran none — and settling that with `pytest` (the correct binary, per W29f) is a clean bounded run for a successor.
