<!-- collected 2026-09-08T03:44:21Z by campaign coordinator; agent id a36a3b36b2265d83b; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a36a3b36b2265d83b.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W06i**, lane 6 (mortality-paper independence claim), OPUS-CAPACITY-CAMPAIGN-20260908. Successor to W06h. Container checkout `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as `claude-opus-5`. Nothing I can run in this container verifies the served model; the coordinator must extract the actual per-child runtime model from the transcript.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:38:16 UTC 2026` | `Tue Sep  8 03:41:11 UTC 2026` |
| `git rev-parse HEAD` | `1c9d827870599576c0c027a9134363d59456fd04` | `5ae0fa04ff9516ac8f820381079d644a094f4a77` |
| `git status --porcelain` | *(empty)* | *(empty, 0 lines)* |

HEAD advanced under me (coordinator collecting reports). All census greps in the Result section were run at `5ae0fa04`, recorded in the Validation section; nothing I read is a manuscript or generator file, so the move does not affect the census (the moving files are campaign reports, which I excluded by pathspec).

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start:

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

Scratch directory `/tmp/claude-0/w06i` was created and **deleted** (`rm -rf`; `ls` afterwards returns `No such file or directory`). No repository write, no git write operation, no manuscript edit. I did not run `scripts/preflight.sh`, did not re-derive the mortality estimates, did not re-run E4, and never invoked `research/modalities/atr_hrd_sarcoma_series.py`.

## Question

W06h refuted, by execution, four sentences claiming the relative-survival artifact and the registry cause split "share no input", and established the narrowed claim that survives: the two **estimates** share no numeric ingredient. It named six live printings.

**My question, read-only and bounded:** is that census complete? Specifically —

1. How many printings of the refuted shared-input claim exist across the whole tracked tree, in any wording?
2. Which are hand-written source strings and which are generated files that would be overwritten if edited directly — and for the generated ones, which script and which exact source `file:line` must change instead?
3. Does any gate, test or lint assert the refuted wording, so that the repair would turn a check red?
4. Is W06h right that this is prose-scope with no effect on any published number — i.e. is any pinned quantity in `pinned-figures.json` keyed to these sentences?

It is open because W06h's dispatch stopped at the sentences it was pointed at. A repair applied to six locations when more exist leaves the refuted claim in the tree, and a repair applied to a generated file is silently undone by the next regeneration.

## Prior-work check

Read in full first: `COMMON-BRIEF.md` (93 lines), `CORPUS-CONTEXT.md` (73), `CLOSED-WORK.md` (70), and `reports/W06h-mortality-successor.md` (371 lines, read via its saved tool-result capture; all nine sections). I am not replaying:

- **W06h** — I do not re-run its perturbation matrix, do not re-derive the life-table cache, do not re-open E4, and I take its verdict table (six of ten sentences survive; four refuted as written) as given rather than re-adjudicating it. I extend exactly the one item it named as its successor: the consumer census.
- **W06g** — its same-value collision matrix and re-labels are untouched.
- **W06e** — the 1.77 margin-to-reversal question is untouched.
- **W25** — not read, not referenced.
- `CLOSED-WORK.md` — I introduce no new cohort, no source retrieval, no denied-route replay; I touched the network zero times.

Campaign reports are **not** repository evidence, so every census grep carries the pathspec `':!research/autonomy/opus-capacity-campaign-20260908/**'`. The two `what_it_would_claim` hits that came back inside W09d/W09e/W09f reports are sibling reports, not prior art, and I did not rely on them; I re-established the generator link from `systems/systems_check.py` directly.

## Method and inputs

Live checkout only (`/home/user/Rare-cancers`); I did not read the frozen corpus at `/tmp/claude-0/frozen-corpus/`, because this is a *census of the current tracked tree* and a `93b`-era snapshot would answer a different question. That is a deliberate scope choice, recorded as a limitation.

Tooling: `git grep -n -i -E` over tracked files with the campaign pathspec excluded, `git ls-files`, `sed -n`, `grep -n`, `python3` (3.11) for the `pinned-figures.json` scan. No execution of any repository generator.

**Patterns searched, verbatim, so recall can be judged:**

| # | Regex (case-insensitive, `git grep -n -i -E`) | Purpose |
|---|---|---|
| P1 | `shar(e\|es\|ing\|ed)[^.]{0,40}no (shared )?inputs?` | the canonical wording, all inflections |
| P2 | `none of (its\|the\|their)[^.]{0,20}inputs?\|no common inputs?\|no overlapping inputs?\|disjoint inputs?\|independent inputs?\|input.{0,15}in common\|nothing in common` | the "shares none of its inputs" variant and near-synonyms |
| P3 | `(two\|are\|wholly\|fully\|entirely\|statistically\|methodologically) independent (methods?\|estimates?\|checks?\|measurements?\|approaches?\|analyses\|lines?\|sources?\|routes?)\|independent (of the )?cause.split\|independent method` | independence framing (too broad tree-wide; refined as P3b) |
| P3b | `independen[a-z]*` piped through a second filter for `cause.split\|relative survival\|competing (share\|fraction\|mortality)\|cause attribution` | independence wording *in this subject area* |
| P4 | `(do(es)? not\|don't\|doesn't\|never\|cannot\|can't) shares?[^.]{0,40}(input\|data\|source\|number\|figure)` | negated-verb phrasing |
| P5 | `no inputs? in common\|inputs? in common\|zero shared\|entirely separate inputs?\|separate inputs?\|wholly separate` | "separate inputs" phrasing |
| P6 | `what_it_would_claim` / `The paper would claim` in `systems/systems_check.py` | establish the generator link |
| P7 | `git ls-files \| grep -i mortality` | find any second copy / SI / submission variant of the paper |
| P8 | `two (methods\|routes\|ways\|estimates\|figures\|numbers)` filtered for `input\|independ\|cause\|surviv` | the "the two methods…" construction independent of the word *share* |

Plus targeted reads: `systems/systems_check.py:3040-3050`, `:3230-3240`, `:4530-4546`; `research/manuscripts/emc_relative_survival.py:35,178,208-215,225-232`; front-matter of `research/IDEAS.md`, `systems/views/L2-rt-competing-mortality.md`, `systems/views/L3-publications.md`, `research/manuscripts/emc-relative-survival.json`; `research/manuscripts/emc-mortality-mechanisms-paper.md:78-82,160-164,254-258`; `research/autonomy/research-ledger.json:316`; `research/manuscripts/tests/test_emc_mortality_decomposition.py`; `research/manuscripts/pinned-figures.json`.

## Result

### R1. The census is incomplete. Six named; **fifteen** printings exist across **eleven** files.

`PRIMARY` (all rows verified by direct read of the cited line at `5ae0fa04`).

**Hand-written source strings carrying the refuted claim — 7 locations, 4 files. These are what the paper owner edits.**

| # | `file:line` | Claim as written (trimmed) | In W06h's six? |
|---|---|---|---|
| H1 | `research/manuscripts/emc-mortality-mechanisms-paper.md:80` | "…against 21.7 per cent from the cause split; **the two methods share no input.**" | yes |
| H2 | `research/manuscripts/emc-mortality-mechanisms-paper.md:162` | "it is independent of the cause-split described above and **shares none of its inputs**" (second clause only) | yes |
| H3 | `research/manuscripts/emc-mortality-mechanisms-paper.md:256` | "**The two share no input**: one is published all-cause survival divided by a national life table…" (first clause only) | yes |
| H4 | `research/IDEAS.md:166` | "…a figure relative survival and registry cause attribution **agree on despite sharing no input**…" | yes |
| H5 | `research/manuscripts/emc_relative_survival.py:229` | Python string literal: `"share no input: one is published all-cause survival divided by a national life "` | yes (named as "the `reading` string") |
| **H6** | **`systems/graph/publications.json:573`** | `PUB-MORTALITY-MECHANISM.what_it_would_claim`: "…a figure relative survival and registry cause attribution **agree on despite sharing no input**…" | **NO — missed** |
| **H7** | **`systems/graph/publications.json:579`** | `PUB-MORTALITY-MECHANISM.outcome_potential_why`: "…agreed on by relative survival and registry cause attribution **despite sharing no input**…" | **NO — missed** |

**Generated files carrying the refuted claim — 8 locations, 8 files. Editing any of these directly is overwritten.**

| # | `file:line` | Producing script | Source string that must change instead | In W06h's six? |
|---|---|---|---|---|
| G1 | `research/manuscripts/emc-relative-survival.json:210` (`convergence.reading`) | `research/manuscripts/emc_relative_survival.py` | **`emc_relative_survival.py:229`** (= H5) | yes |
| G2 | `systems/views/L2-rt-competing-mortality.md:80` | `systems/systems_check.py` (emit site `:3045`) | **`systems/graph/publications.json:573`** (= H6) | yes |
| **G3** | **`systems/views/L2-rt-early-palliative.md:93`** | `systems/systems_check.py:3045` | `systems/graph/publications.json:573` | **NO — missed** |
| **G4** | **`systems/views/L2-rt-host-factor.md:66`** | `systems/systems_check.py:3045` | `systems/graph/publications.json:573` | **NO — missed** |
| **G5** | **`systems/views/L2-rt-respiratory-failure.md:81`** | `systems/systems_check.py:3045` | `systems/graph/publications.json:573` | **NO — missed** |
| **G6** | **`systems/views/L2-rt-treatment-harm.md:83`** | `systems/systems_check.py:3045` | `systems/graph/publications.json:573` | **NO — missed** |
| **G7** | **`systems/views/L2-rt-vte-prophylaxis.md:92`** | `systems/systems_check.py:3045` | `systems/graph/publications.json:573` | **NO — missed** |
| **G8** | **`systems/views/L3-publications.md:294`** | `systems/systems_check.py` (emit site **`:3238`**) | `systems/graph/publications.json:573` | **NO — missed** |

**W06h named two generated consumers; there are eight.** The reason the count is six-fold larger is structural and is the substantive finding of this unit: `PUB-MORTALITY-MECHANISM.what_it_would_claim` is rendered into **every L2 route view whose route feeds that publication**, not only the one route view whose subject is competing mortality. Six route views (`competing-mortality`, `early-palliative`, `host-factor`, `respiratory-failure`, `treatment-harm`, `vte-prophylaxis`) plus the L3 publications index all carry the same sentence verbatim. One edit to `publications.json:573` plus `--write-views` fixes all seven; seven separate view edits fix none of them durably.

**Generator link, established by direct read, not inferred:**

```
systems/systems_check.py:3045:   f"**The paper would claim:** {p['what_it_would_claim']}\n"]
systems/systems_check.py:3238:   out += ["**" + " · ".join(bits) + "**\n", p["what_it_would_claim"], ""]
```

and the front matter of every one of the seven view files declares `kind: generated`, `status: generated`, `generator: systems/systems_check.py`.

`publications.json:579` (`outcome_potential_why`, H7) is a hand-written printing with **no** generated consumer: `grep -rn "outcome_potential" systems/systems_check.py` returns only `:4376` and `:4471`, both of which read `p["outcome_potential"]` (the band) and never `outcome_potential_why`. So H7 must be repaired on its own; nothing regenerates it and nothing propagates it.

### R2. Hits that look like the refuted claim and are **not** — recorded so the owner does not over-correct

`PRIMARY`, read in full at the cited line.

| `file:line` | Text | Why it is not the refuted claim |
|---|---|---|
| `emc-mortality-mechanisms-paper.md:10` | front-matter: "the convergence of relative survival and registry cause attribution as **independent estimates** of competing mortality" | scoped to *estimates* — W06h's surviving scope. Leave. |
| `emc-mortality-mechanisms-paper.md:162` first clause | "it is **independent of the cause-split** described above" | verified by W06h's E4. Only the second clause is refuted. |
| `emc-mortality-mechanisms-paper.md:256` second clause | "neither can be derived from the other" | survives (E4, both directions). |
| `emc-relative-survival.json:189` ← `emc_relative_survival.py:212` | "Relative survival and the cause-split are INDEPENDENT. One never touches a cause of death…" | estimator-scoped; W06h graded it SURVIVES. |
| `emc_relative_survival.py:35` (docstring) | "it is INDEPENDENT of the cause-split" | estimator-scoped. Survives. |
| `emc_relative_survival.py:178` (comment) | "# The independent comparator: the cause-split…" | estimator-scoped, though it sits immediately above the code that opens the cause-split artifact as an input. Cosmetically ironic, not false. |
| `emc-terminal-events.json:39` | "they converge with the registry cause-split **computed separately**" | "computed separately" is true (different generator). Not a shared-input claim. |
| `systems/graph/routes.json:8932` → `systems/views/L2-rt-competing-mortality.md:46` | "relative survival **independently** gives 23.0%" | estimator-scoped. Survives. Note it *is* a hand-written→generated pair if the owner ever decides to soften it. |
| `research/autonomy/research-ledger.json:316` | the 1.77 / (0.97, 1.04) corroborating-pair presentation W06h flagged | a *presentation* problem, not a shared-input sentence. Out of scope for this repair; retained as W06h left it. |
| `research/manuscripts/emc-mortality-mechanisms.md` (the memo), `systems/views/L1-st-mortality-mechanism.md` | — | **clean.** No printing of the claim in either. |

`git ls-files | grep -i mortality` returns 14 paths and confirms there is **no** second copy, SI, or submission variant of the mortality paper in the tree. The census is over one manuscript.

### R3. No gate, test or lint asserts the refuted wording — but the repair is mechanically coupled to one gate

`PRIMARY, and it is a negative finding stated as such.`

`git grep` for the wording restricted to `scripts/`, `systems/tests/`, `research/manuscripts/lint_*.py`, `'*test*'` and `.github/**` returned **zero hits**. The only test touching these artifacts is `research/manuscripts/tests/test_emc_mortality_decomposition.py`, and every assertion in it is numeric (`competing_share_of_deaths_pct` values, band non-negativity, `None` for undefined shares); it asserts nothing about `reading`, `⭐_why_this_matters`, independence, or any prose string. **No check goes red because a sentence stops claiming the two methods share no input.**

One coupling the owner must nevertheless honour, and it is a gate — `systems/systems_check.py:4536`:

```python
def check_views(g, f):
    """A generated view that has been hand-edited, or has drifted from the graph, is a defect."""
    ...
        f.err("[G1]", f"generated view missing: systems/views/{rel} — run --write-views")
    ...
        f.err("[G2]", f"systems/views/{rel} differs from what the graph renders — it was "
                      f"hand-edited or the graph moved. Run --write-views.")
```

So: editing any of G2-G8 directly turns `[G2]` **red**, and editing `publications.json:573` **without** running `python3 systems/systems_check.py --write-views` also turns `[G2]` red for all seven views at once. This is not the check asserting the refuted claim; it is the check that makes the generated/hand-written distinction in R1 load-bearing rather than advisory. The equivalent obligation on the other side is regenerating `emc-relative-survival.json` after editing `emc_relative_survival.py:229` — I found no drift check enforcing that one, so a stale `emc-relative-survival.json` would pass silently. That asymmetry is worth the owner's attention but is outside my repair-free scope.

### R4. W06h's "no effect on any published number" — **CONFIRMED**

`PRIMARY.` `research/manuscripts/pinned-figures.json` is a 10-key dict (`_README`, `targets`, `_marker_note`, `supersession_markers`, `derivations`, `artifact_figures`, `table_completeness`, `superseded`, `subset_checks`, `_artifact_figures_note`). Serialised to a single JSON string and scanned:

| token | occurrences in `pinned-figures.json` |
|---|---|
| `21.7` | 0 |
| `23.0` | 0 |
| `1.77` | 0 |
| `0.97` | 0 |
| `share no input` | 0 |
| `sharing no input` | 0 |
| `mortality` | 0 |
| `relative survival` / `relative_survival` | 0 |
| `cause split` / `cause-split` | 0 |
| `1.04` | 1 |
| `independen` | 7 |

`grep -n -i "mortality\|relative-surv\|relative_surv"` over the raw file returns **nothing**. The single `1.04` is at `:1854` inside a GPU realised-spend row (`$48.89` / `$126.17` / `+$25.83`), and all seven `independen` hits are unrelated (`:1325` blind review seats, `:1646` score-independent matcher, `:1716` median-of-N-independent-hosts, `:1860` bandwidth heuristic, `:1904` scoring-independent second pose method, `:1928` cross-margin design pairs, `:1952` HLA coverage seats). **No pinned quantity is keyed to any of the fifteen sentences.** The repair is prose-scope, exactly as W06h said, and additionally it does not require a `pinned-figures.json` entry of its own since no pinned figure moves.

## Validation evidence

### RUN

Environment: container `container_0166QEHnXrRA8nCR59c9UG4k`, Linux 6.18.44-fc-v24, `cwd=/home/user/Rare-cancers`, `git rev-parse HEAD = 5ae0fa04ff9516ac8f820381079d644a094f4a77`, `git status --porcelain` = 0 lines at both start and end. Python 3.11. All commands read-only; every `git grep` invocation carried `X=":!research/autonomy/opus-capacity-campaign-20260908/**"`. All exited 0 except where noted.

Census commands, verbatim:

```
git grep -n -i -E "shar(e|es|ing|ed)[^.]{0,40}no (shared )?inputs?" -- . "$X"          # P1 → 13 lines, 11 files
git grep -n -i -E "none of (its|the|their)[^.]{0,20}inputs?|no common inputs?|..."     # P2 → 1 line (unrelated: new-evidence-routes.md:465)
git grep -n -i -E "independen[a-z]*" -- . "$X" | grep -i -E "cause.split|relative survival|..."  # P3b → 11 lines
git grep -n -i -E "(do(es)? not|don't|doesn't|never|cannot|can't) shares?[^.]{0,40}(input|data|source|number|figure)"  # P4 → 5 lines, all unrelated
git grep -n -i -E "no inputs? in common|inputs? in common|zero shared|entirely separate inputs?|..."  # P5 → 4 lines, all unrelated
grep -n "what_it_would_claim\|The paper would claim" systems/systems_check.py          # P6 → :3045, :3238
git ls-files | grep -i "mortality"                                                     # P7 → 14 paths
git grep -n -i -E "two (methods|routes|ways|estimates|figures|numbers)" -- ... | grep -i -E "input|independ|cause|surviv"  # P8 → 27 lines, one in scope (paper.md:80)
```

Gate search, verbatim, **exit 1 / empty output** (the negative in R3):

```
git grep -n -i -E "shar(e|es|ing)[^\"]{0,30}no input|no shared input|share no input" \
  -- scripts systems/tests research/manuscripts/lint_*.py '*test*' '.github/**'
(no output)
```

Generator-link confirmation:

```
grep -rn "outcome_potential" systems/systems_check.py
systems/systems_check.py:4376:  "band": OUTCOME_BAND.get(p.get("outcome_potential"), 1),
systems/systems_check.py:4471:  out.append(f"| {i} | {name} | {BAND_LABEL.get(p.get('outcome_potential'), '?')} | "
```

— i.e. `outcome_potential_why` never appears, which is the evidence for H7 having no generated consumer.

Pinned-figures scan (Python, exit 0), verbatim output:

```
21.7 -> 0
23.0 -> 0
share no input -> 0
sharing no input -> 0
independen -> 7
mortality -> 0
relative_survival -> 0
relative survival -> 0
cause split -> 0
cause-split -> 0
1.77 -> 0
0.97 -> 0
1.04 -> 1
```

Scratch teardown:

```
rm -rf /tmp/claude-0/w06i && ls -d /tmp/claude-0/w06i
ls: cannot access '/tmp/claude-0/w06i': No such file or directory
```

### PROPOSED (NOT RUN)

- `python3 systems/systems_check.py --check` before and after any repair, to confirm `[G2]` is green — **NOT RUN**; I am read-only and running `--check` on a tree I must not modify proves nothing about a repair that does not exist yet. The owner runs it.
- Regeneration diff of `emc-relative-survival.json` after changing `emc_relative_survival.py:229` — **NOT RUN**; that is a repository write.
- `scripts/preflight.sh` — **NOT RUN**, explicitly excluded by my dispatch.

## Limitations

- **Recall is bounded by my eight patterns.** A printing of the claim in wording none of P1-P8 matches (a paraphrase with no form of *share*, *input*, *independent*, *separate* or *common*) would be missed. I judge the residual risk low because the claim reduces to a small vocabulary, and because P3b independently swept every occurrence of `independen*` in the subject area — but "I found fifteen" is not "there are exactly fifteen."
- **Tracked files only, current working tree only.** I did not search `.git` history, untracked files, or the frozen corpus at `/tmp/claude-0/frozen-corpus/`. A printing present at `93b` but absent now is out of scope by design; a printing present in the corpus but not the tree would be UNKNOWN to me, not absent.
- **I excluded the campaign report directory by pathspec.** Sibling reports quote the refuted sentences repeatedly; those quotations are evidence *about* the defect and are not printings to repair. If the coordinator wants them counted, that is a separate pass.
- **I did not verify the generation claims by executing any generator.** The generated/hand-written classification rests on (a) declared front matter `kind: generated, generator: systems/systems_check.py`, (b) the two emit sites read directly at `:3045`/`:3238`, (c) `"generated_by": "research/manuscripts/emc_relative_survival.py"` in the JSON header and the matching string literal at `:229`, and (d) byte-identical text between source and consumer. That is strong documentary evidence, not an execution proof.
- **I did not re-adjudicate W06h's verdicts.** Whether a given sentence is refuted is W06h's finding; my contribution is *where else it is printed*. If W06h's E3/E5 refutation were itself wrong, my census would be a census of sentences that need no repair.
- This unit establishes nothing scientific about EMC. It makes no claim about mortality, efficacy, safety, selectivity or clinical readiness, and touches no patient data.

## Stop condition

**Set up front:** return as soon as (i) the tree-wide census is complete under a set of patterns I can name, (ii) every hit is classified hand-written vs generated with the producing script and source `file:line` for each generated one, (iii) the gate/test/lint question is answered with a `file:line` or an explicit "none found", and (iv) `pinned-figures.json` is checked for keying — or at ~40 tool calls / ~40 minutes, whichever comes first.

**MET**, on all four, at 14 tool calls and 3 minutes. Returning early. No repair authored, no patch drafted, no file edited.

## Tool-call and wall-clock count actually used

**14 tool calls** (11 `Bash`, 2 `Read`, 1 `Grep`). One `Bash` call was refused by the auto-mode classifier (`awk` over a tool-result capture); per protocol I recorded the refusal, did not route around it maliciously, and obtained the same information with `Grep` — the refusal text was: *"Permission for this action was denied by the Claude Code auto mode classifier. Reason: Blocked by classifier."* This was a harness permission classifier, **not** a content-policy refusal, and it cost nothing scientific.

**Wall clock: 2 min 55 s** (`03:38:16Z` → `03:41:11Z`). Budget was ~40 calls / ~40 minutes.

## Next concrete action

**For the paper owner (the repair, which is not mine to make):** the correction has **seven** edit sites, not fifteen — `emc-mortality-mechanisms-paper.md:80`, `:162` (second clause), `:256` (first clause), `research/IDEAS.md:166`, `emc_relative_survival.py:229`, `systems/graph/publications.json:573`, and `systems/graph/publications.json:579` — followed by `python3 systems/systems_check.py --write-views` (which repairs all seven generated views in one pass and keeps `[G2]` green) and a regeneration of `emc-relative-survival.json` from its script. No test or lint asserts the old wording, so nothing goes red for the wording itself; no pinned figure moves. The narrowed claim W06h verified — *the two **estimates** share no numeric ingredient* — is available as replacement text and is true.

**One specific successor task for this lane:** audit the **other** `PUB-*` entries in `systems/graph/publications.json` for `what_it_would_claim` strings whose content has been superseded by later measurement. This lane just demonstrated that a single hand-written field there fans out to seven generated files, so `publications.json` is a high-leverage place for a stale claim to hide, and `what_it_would_claim` is not covered by any drift check that compares it against the artifact it describes — only against the views it renders into. That is a bounded, read-only, tree-local question with a real defect class behind it. (Note for the coordinator: sibling reports W09d/W09e/W09f appear to have worked adjacent ground on `publications.json` field auditing; whoever takes this should read them first to avoid a replay — I did not, because campaign reports are not repository evidence and reading them was outside my unit.)
