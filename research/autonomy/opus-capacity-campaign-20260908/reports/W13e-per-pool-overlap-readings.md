> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

## Worker

**W13e** — lane 13 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`); nothing in my environment independently confirms a served model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 02:34:57 UTC 2026` · `date -u` **end**: `Tue Sep  8 02:36:56 UTC 2026`

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start of run):

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
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 -Djavax.net.ssl.trustStorePassword=changeit -Djavax.net.ssl.trustStoreType=PKCS12 -Dhttps.proxyHost=127.0.0.1 -Dhttps.proxyPort=37223 -Dhttp.nonProxyHosts=... -Djdk.http.auth.tunneling.disabledSchemes= -Djdk.http.auth.proxying.disabledSchemes=
NO_PROXY=localhost,127.0.0.1,::1,...
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

(The two long proxy variables are elided with `...` only where they repeat the `no_proxy` list verbatim; nothing else is altered.)

**Actual HEAD read**: `7d081218f107363573573e6d102e4334567adf77` ("Campaign: fourth batch of worker reports (61 collected)"). **This is NOT the `92abbcb905cacf07f14b238db50d1b98f6590374` named in COMMON-BRIEF.md** — that commit is now 4 commits back (`92abbcb9` → `103ff76f` → `b9a0257e` → `47aac85f` → `7d081218`). All four intervening commits touch only campaign report/log files, not `research/modalities/` or the registry; I record the divergence rather than assuming it is harmless.

I wrote nothing into the Git working tree. My only writes were `/tmp/claude-0/w13e/both_readings.py`. During my run `research/autonomy/opus-capacity-campaign-20260908/WAVE-LOG.md` became modified in the tree (a `~02:40Z`-stamped correction section); **that is not mine** — my first `git status --porcelain` was empty and I ran no editor on the tree.

## Question

**Is the per-pool reading that `research/modalities/emc_site_curation.py` relies on defensible from committed evidence, and what exactly would change if the `bishop2019` `pool: false` exclusion travelled with the source instead?**

Open because W13d identified `research/modalities/emc-site-curation.json` as the single artifact exposed to the choice, but did not measure whether the argument the generator gives for its choice is anchored in any committed field, nor put the two readings side by side with their intervals.

I make **no determination about what any cohort `n` counts** (W13c resolved that; W13b owns the remainder). Every `n` below is transcribed as committed, with no unit reading attached. I endorse **neither** reading.

## Prior-work check

Commands run (all read-only, from `/home/user/Rare-cancers`):

- `wc -l COMMON-BRIEF.md CLOSED-WORK.md CORPUS-CONTEXT.md` → 84 / 70 / 63 lines; all three read in full.
- `ls .../reports/` → 61 files. `W13-provenance-identity-contract.md` (538 l), `W13b-pooled-cohort-unit-resolution.md` (428 l), `W13c-remaining-cohort-units.md` (551 l), `W16b-frechet-followup-adversarial.md` (314 l) are present.
- **`W13d-*.md` DOES NOT EXIST at this HEAD.** `cat W13d-*.md` → `cat: 'W13d-*.md': No such file or directory` (exit 1); `find / -name 'W13d*' -not -path '*/proc/*'` → **no hits anywhere on the filesystem**, including the frozen corpus. W13d's report has not yet been collected. **Everything I attribute to W13d comes from my dispatch prompt, not from a file I read.** That is a transfer limit, not a verification.
- `grep -rn -i "bishop" --include='*.json' --include='*.py' --include='*.md' . | grep -i -E "overlap|double-count|partner|dedup|same population|within SEER"` — the whole tree, plus the same grep over `/tmp/claude-0/frozen-corpus/extracted/corpus/`.
- `grep -rn -o -E '"(populationKey|overlapsWith|overlapPartner|overlapWith|partnerId|supersededBy|dedupKey|cohortKey)"' --include='*.json' .`

**CLOSED-WORK items confirmed not replayed**: I did not touch PUB-EMC-CLASSIFICATION (user-rejected), any Brenca route, any patient/case/specimen identity question, `GSE4303`/`GSE28866`, the NR4A Perspective, or any denied-route source fetch. **No network was used at all.** I did not re-run W16b's Fréchet computation or W16's admissibility rule; I only read W16b's committed report for framing consistency. Frozen corpus consulted for the absence claim in §3 below; its `snapshot-provenance.json` caveat applies (absence there is not repository-wide absence).

## Method / inputs

| Input | Path | Role |
|---|---|---|
| Generator | `/home/user/Rare-cancers/research/modalities/emc_site_curation.py` (38 KB) | subject; source of the verbatim rationale |
| Artifact | `/home/user/Rare-cancers/research/modalities/emc-site-curation.json` | committed figures |
| Registry | `/home/user/Rare-cancers/research/data/emc-clinical-registry.json` | `cohorts[5]` (`bishop2019`), `cohorts[0..4]`, `citations` |
| Policy | `/home/user/Rare-cancers/systems/POLICY-evidence.md` §§ scope, 2.1, 2.2, **2.3**, 2.6, 2.7(d), 5 | binding contract |
| Enforcement | `/home/user/Rare-cancers/scripts/validate-registry.mjs`, `/home/user/Rare-cancers/scripts/preflight.sh`, `/home/user/Rare-cancers/research/modalities/tests/test_emc_site_curation.py` | what actually checks what |
| Frozen corpus | `/tmp/claude-0/frozen-corpus/extracted/corpus/` (read-only, not overlaid, not copied) | absence check |
| Scratch | `/tmp/claude-0/w13e/both_readings.py` | the only file I authored |

Tooling: `python3` (system, `/usr/local/bin/python3`), `git`, `grep`. `pytest` is **not installed** in this container.

## Result

### 1 · The generator's own stated rationale, verbatim

From `emc_site_curation.py`, key `"⭐_why_bishop2019_is_pooled_HERE_and_pool_false_in_the_REGISTRY"` (reproduced byte-identically in the committed artifact at `emc-site-curation.json:11`):

> "The clinical registry marks bishop2019 `pool: false` with `contextReason: population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)`. That exclusion bites only where an overlap PARTNER is inside the same pool, and neither SEER nor the US Sarcoma Collaborative contributes a site distribution to this one. ⛔ Pool membership is decided per pool, not once per source. The registry's recurrence and metastasis pools do contain ussc2022, so its flag stands unchanged there."

And the module docstring, lines 35-36:

> "`⚠_SUPERSEDED_the_other_nine_series`. bishop2019 (n=41) joins the site pool; drilon2008 is recorded as context and pooled into nothing, because its site distribution is printed only as percentages."

The generator also states its policy anchor for the *pairing*, in `_method.⚠_what_is_pooled`:

> "POLICY-evidence §2.3 names exactly this pairing — 'a Japanese registry and a US single institution' — as distinct populations that may be pooled."

### 2 · Regeneration fidelity — **ESTABLISHED** (`PRIMARY`)

`python3 research/modalities/emc_site_curation.py --check` → `OK: emc-site-curation.json matches the generator`, **exit 0**. The committed artifact is byte-reproducible from committed inputs; `--check` writes nothing (`git status --porcelain` unchanged for that path). All series counts are hard-coded constants in the generator, so "committed inputs" means the generator's own transcribed tables — there is no external data file to drift.

### 3 · Both readings, side by side — **NEITHER ENDORSED**

Computed by `/tmp/claude-0/w13e/both_readings.py`, which imports the real module and re-uses its own `_row()` and `wilson()` without modification; the only difference between the two columns is the membership list passed in. Wilson score 95%, crude denominator-weighted proportion, exactly as the file computes them.

| Reading | Pool members | Definition | events | denom | percent | Wilson 95% | Status |
|---|---|---|---|---|---|---|---|
| **A — per-pool** | chiusole2020, masunaga2025, **bishop2019** | strict | 194 | 271 | **71.6%** | 65.9 – 76.6 | **COMMITTED** (`PRIMARY`) |
| **A — per-pool** | chiusole2020, masunaga2025, **bishop2019** | inclusive | 229 | 271 | **84.5%** | 79.7 – 88.3 | **COMMITTED** (`PRIMARY`) |
| **B — travels with the source** | chiusole2020, masunaga2025 | strict | 162 | 230 | **70.4%** | 64.2 – 76.0 | NOT committed (`SECONDARY`) |
| **B — travels with the source** | chiusole2020, masunaga2025 | inclusive | 197 | 230 | **85.7%** | 80.5 – 89.6 | NOT committed (`SECONDARY`) |

Per-cohort rows, unchanged between readings: `chiusole2020` 78.0% (both definitions), `masunaga2025` 67.8% strict / 88.3% inclusive, `bishop2019` 78.0% (both).

**Two findings worth the registry owner's attention, both bookkeeping:**

1. **Reading B reproduces the file's own retained superseded figures exactly.** `⚠_superseded_retained.pooled_extremity_fraction_2026_08_25` records "70.4% (64.2-76.0) strict and 85.7% (80.5-89.6) inclusive, over 230 patients in two series". My independent recomputation returns 70.4 (64.2-76.0) and 85.7 (80.5-89.6) over 230. So the travels-with-the-source reading requires **no new computation and invents no number** — the artifact already carries its result verbatim, labelled as the superseded state. Switching readings would be a *revert to a retained figure*, not a recalculation.
2. **The two readings differ by ~1.2 pp strict and ~1.2 pp inclusive, in opposite directions, and every interval overlaps heavily.** The file discloses this direction itself: "Adding a third series moved the strict reading UP and the inclusive reading DOWN, which narrows the gap between the two definitions without closing it. The gap remains the binding uncertainty." **The strict-vs-inclusive gap (≈13 pp) is an order of magnitude larger than the reading choice (≈1.2 pp).** I state that as a measured comparison of the four numbers, not as an argument that the reading choice does not matter — a rule question is not settled by the size of its numerical consequence, and that judgement belongs to the registry/policy owner.

### 4 · What the per-pool argument actually depends on — **the counterpart is UNKNOWN** (`UNKNOWN`)

The generator's argument has the form: *the exclusion bites only where an overlap PARTNER is inside the same pool; neither SEER nor USSC is in this pool; therefore it does not bite here.* That argument needs a **named counterpart set**. I measured whether any committed field supplies one.

`bishop2019`'s registry row, `research/data/emc-clinical-registry.json` → `.registry.cohorts[5]`, complete:

```
label: "Localised, single-institution series"    n: 41    pool: false
sourceId: "bishop2019"    provenance: "primary"    studyPeriod: [1990, 2016]
contextReason: "population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)"
note: "41 consecutive localized EMC; 5/41 (12%) local relapse; 10-yr local control 100% with
       surgery+radiotherapy vs 63% surgery alone (HR 12.7). Not pooled to avoid double-counting
       the US population."
```

**There is no `populationKey` on this row.** `populationKey` exists in the registry at exactly five places, all on `pool: true` rows, and each value is essentially the row's own source identity:

| path | sourceId | pool | populationKey |
|---|---|---|---|
| `.registry.cohorts[0]` | masunaga2025 | true | `masunaga2025-jpreg` |
| `.registry.cohorts[1]` | masunaga2025 | true | `masunaga2025-jpreg` |
| `.registry.cohorts[2]` | meisKindblom1999 | true | `meisKindblom1999` |
| `.registry.cohorts[3]` | ussc2022 | true | `ussc2022` |
| `.registry.cohorts[4]` | chiusole2020 | true | `chiusole2020` |

No two *different* sources share a key; no `pool: false` row carries one. There is no `overlapsWith`, `overlapPartner`, `partnerId`, `dedupKey` or `cohortKey` field anywhere in any tracked JSON (the grep returns only `populationKey` hits, in the registry and in `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json`).

Searching the entire tree **and** the frozen corpus for any text linking `bishop2019` to an overlap partner returns exactly **two** places, and they are the same statement twice:

- `research/data/emc-clinical-registry.json` — the hedged free-text `contextReason` above, and the free-text `note` ("the US population");
- `research/modalities/emc-site-curation.json:11` / `emc_site_curation.py` — the generator **quoting that same `contextReason` back**.

No third, independent committed field asserts a shared population between `bishop2019` and `ussc2022`, `seer270_2022`, or anything else.

**Therefore: the counterpart set of `bishop2019`'s overlap is UNKNOWN from committed fields.** The only committed statement is hedged — the word is *"likely"* — and the registry does not commit to it: it names no key, no partner id, and no structured link. **I do not infer a counterpart from cohort size, country, study period, authorship or institution**, and I note explicitly that `bishop2019`'s `studyPeriod [1990, 2016]` overlapping `ussc2022`'s `[2000, 2016]` is **not** used here as evidence of anything — date overlap is not population overlap, and treating it as such would be exactly the inference the brief forbids.

**Consequence for the per-pool argument, stated as a dependency and not as a verdict:** the argument's premise ("neither SEER nor the US Sarcoma Collaborative contributes a site distribution to this pool") is *checkable and true as stated* — `ussc2022` and `seer270_2022` are indeed absent from `SERIES` in the generator. But the argument's *scope* — that those two are the whole counterpart set, so their absence discharges the exclusion — rests on reading a hedged free-text phrase as an exhaustive enumeration. The registry does not commit to that enumeration. If the true counterpart set is wider than the phrase's two named registries, the per-pool argument does not reach it. **Whether that gap matters is the owner's call, not mine.**

### 5 · What POLICY-evidence actually says, and what enforces it (`PRIMARY`)

Read before any pooling conclusion, as required. §2.3, verbatim, the across-studies clause:

> "**Across studies:** single-institution series are often subsets of national or SEER registries. Where populations may overlap, the **smaller/overlapping** cohort is marked `pool: false` with `contextReason: "population-overlap"`. Distinct populations (e.g. a Japanese registry and a US single institution) may be pooled."

Two observations, both textual:

- **§2.3 phrases the marking as a property of the cohort**, not of a pool: "*the smaller/overlapping cohort is marked `pool: false`*". The word "pool" appears nowhere in that sentence as a scope qualifier. **§2.3 does not say pool membership is decided per pool; it also does not say it is decided once per source.** The per-pool reading is a *construction* on top of §2.3, and it is the generator that supplies it — the sentence "⛔ Pool membership is decided per pool, not once per source" appears in `emc_site_curation.py`, **not** in `POLICY-evidence.md`. I checked: the phrase occurs nowhere in the policy file.
- **The generator cites §2.3's second sentence for its pairing**, and that citation is accurate — "a Japanese registry and a US single institution" is §2.3's own worked example of a poolable pair. But that example licenses `masunaga2025` + a US single institution *in the abstract*; it does not address a US single institution that the registry has separately flagged. **Both clauses of §2.3 apply to `bishop2019` at once, and §2.3 does not order them.** That is the whole ambiguity, and it is a genuine gap in the policy text rather than a violation by either party.

**Scope**: the policy's own front-matter scope is "Clinical and epidemiological evidence only — the EMC registry, the manuscript's meta-analysis, and **any pooled proportion or interval derived from published cohorts**." The site pool is a pooled proportion derived from published cohorts, so **it is in scope**. §2.7(d) reinforces the cohort-property reading for the third estimand class: "the smaller of any overlapping pair stays `pool: false` with its reason recorded."

**But nothing enforces it here** (`PRIMARY`, measured):

- `scripts/validate-registry.mjs` — gate 10 of preflight — reads **exactly one file**: `join(root, "research", "data", "emc-clinical-registry.json")`. It never opens `research/modalities/`. So no gate compares the site pool's membership against the registry's `pool` flags.
- `research/modalities/tests/test_emc_site_curation.py` has 8 tests. `test_context_rows_are_never_pooled_into_any_fraction` asserts only that `pooled_ids == {s["source_id"] for s in mod.SERIES}` — i.e. that the artifact matches the generator's own `SERIES` list. **No test reads the registry, and no test asserts anything about `pool: false`.** The divergence is documented in free-text keys and checked by nothing.

That is the concrete, actionable bookkeeping finding: **the per-pool reading is currently a per-file editorial decision recorded in prose, with no cross-file invariant either enforcing or forbidding it.** Whichever reading the owner picks, that hole stays open until something reads both files.

### 6 · Consistency with W16b — **CONSISTENT, and the two framings compose** (`SECONDARY`)

W16b (`reports/W16b-frechet-followup-adversarial.md`, §2 and §3) reached the identical clause from the admissibility direction. Its verbatim position:

> "It fails **exactly one** clause: `pool == false`, with `contextReason: population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)`. **I did not relax the rule, so bishop2019 is NOT admitted.** I note without acting on it that the repository's own `emc-site-curation.json` argues *'Pool membership is decided per pool, not once per source'* and does pool bishop2019 for site — and that W16's bound never pools, so the double-counting hazard the flag guards against does not arise here. **Changing the acceptance criterion is not mine to do**; I flag it as the one substantive question for whoever owns that rule."

Consistency assessment:

| Dimension | W16b | W13e (this report) | Consistent? |
|---|---|---|---|
| Which clause is at issue | `pool == false` on `bishop2019`, the single failing clause | same | **yes** |
| Verdict authority | "not mine to do" — routed to the rule owner | decision-support package, no decision | **yes** |
| Action taken on the flag | none; W16b computed a Bishop row but labelled it **NOT ADMITTED**, `SECONDARY`, outside the admitted set | none; both readings reported, committed one identified, neither endorsed | **yes** |
| Direction of approach | admissibility: *may this row enter my bound?* → **no** | provenance: *is the file that already used it defensible?* → **UNKNOWN, owner's call** | complementary, not contradictory |
| Treatment of the per-pool argument | quoted, explicitly "without acting on it" | quoted, dependency measured, not endorsed | **yes** |

**They also compose into one observation neither made alone.** W16b's reason for why the flag's hazard does not arise in *its* setting is structural — *"W16's bound never pools"* — and needs no counterpart to be named. The site file's reason is different in kind: it *does* pool, and discharges the flag by asserting the counterpart set is absent from its pool. **W16b's escape does not depend on the counterpart being known; the site file's does.** So the UNKNOWN I record in §4 bites the site-curation argument and leaves W16b's untouched. Read together, the two reports say the same thing to the rule owner from both sides: the flag is a one-bit field carrying a hedged, unenumerated, unenforced claim, and two independent consumers had to invent their own scoping rule to use it.

W13d's related conclusion (per my dispatch, **file not on disk, unverified by me**) — that neither property is required by policy, so both are **PROPOSED NEW REQUIREMENTS, not violations** — is consistent with what I read in §2.3 and §5: §5's checklist item is "*Overlapping / percentage-only / different-endpoint series set `pool:false` + `contextReason`*", which constrains the registry row and says nothing about downstream consumers.

## Validation evidence

**RUN** — all commands executed from `/home/user/Rare-cancers` at HEAD `7d081218f107363573573e6d102e4334567adf77`, `python3` = `/usr/local/bin/python3` (system), no network.

1. Regeneration fidelity:

```
$ python3 research/modalities/emc_site_curation.py --check
OK: emc-site-curation.json matches the generator
EXIT=0
```

2. Committed pooled block, read straight from `research/modalities/emc-site-curation.json` (abridged to the load-bearing fields; full output in transcript):

```
extremity_strict:    events 194, denom 271, percent 71.6, ci95 65.9-76.6
                     per_cohort_percent: chiusole2020 78.0, masunaga2025 67.8, bishop2019 78.0
extremity_inclusive: events 229, denom 271, percent 84.5, ci95 79.7-88.3
                     per_cohort_percent: chiusole2020 78.0, masunaga2025 88.3, bishop2019 78.0
estimator: "crude denominator-weighted proportion (POLICY-evidence §2.2)"
interval:  "Wilson score, 95%"
```

3. Both readings side by side — `/tmp/claude-0/w13e/both_readings.py`, exit 0, `git status --porcelain` showing no change to any `research/` path. Script reproduced in full (it is the only code I authored):

```python
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location(
    "esc", "/home/user/Rare-cancers/research/modalities/emc_site_curation.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def pool(series, inclusive):
    rows = [m._row(s, inclusive) for s in series]
    ev = sum(r["events"] for r in rows); dn = sum(r["denom"] for r in rows)
    p, lo, hi = m.wilson(ev, dn)
    return {"members": [r["source_id"] for r in rows], "events": ev, "denom": dn,
            "percent": round(100*p,1), "ci95_lo_percent": round(100*lo,1),
            "ci95_hi_percent": round(100*hi,1),
            "per_cohort_percent": {r["source_id"]: r["percent"] for r in rows}}
per_pool = m.SERIES
travels = [s for s in m.SERIES if s["source_id"] != "bishop2019"]
out = {"READING_A_per_pool_COMMITTED": {"strict": pool(per_pool, False), "inclusive": pool(per_pool, True)},
       "READING_B_travels_with_source_NOT_COMMITTED": {"strict": pool(travels, False), "inclusive": pool(travels, True)}}
print(json.dumps(out, indent=2, ensure_ascii=False))
```

Verbatim key output:

```
READING_A_per_pool_COMMITTED.strict:      members [chiusole2020, masunaga2025, bishop2019]
                                          events 194, denom 271, percent 71.6, ci95 65.9-76.6
READING_A_per_pool_COMMITTED.inclusive:   events 229, denom 271, percent 84.5, ci95 79.7-88.3
READING_B_travels_with_source.strict:     members [chiusole2020, masunaga2025]
                                          events 162, denom 230, percent 70.4, ci95 64.2-76.0
READING_B_travels_with_source.inclusive:  events 197, denom 230, percent 85.7, ci95 80.5-89.6
EXIT=0
```

4. Counterpart search, exit 0, **no hit beyond the registry's own `contextReason`/`note` and the generator quoting it** — over both the working tree and `/tmp/claude-0/frozen-corpus/extracted/corpus/`:

```
$ grep -rn -o -E '"(populationKey|overlapsWith|overlapPartner|overlapWith|partnerId|supersededBy|dedupKey|cohortKey)"' --include='*.json' .
./research/data/emc-clinical-registry.json:392,420,439,463,483: "populationKey"      (5 hits, all pool:true)
./research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json:356,385,411,423,479
(no overlapsWith / overlapPartner / partnerId / dedupKey / cohortKey anywhere)
```

5. Enforcement scope:

```
$ grep -n "readFileSync\|\.json" scripts/validate-registry.mjs | head -15
24:const REGISTRY = join(root, "research", "data", "emc-clinical-registry.json");
32:  d = JSON.parse(readFileSync(REGISTRY, "utf8"));
$ grep -rn "emc-site-curation\|emc_site_curation" --include='*.mjs' --include='*.sh' .
(no hits — neither preflight nor any .mjs gate references the file)
```

**BLOCKED (attempted, could not run)** — the artifact's own test module:

```
$ timeout 300 python3 -m pytest research/modalities/tests/test_emc_site_curation.py -q
/usr/local/bin/python3: No module named pytest
EXIT=1
```

`pytest` is not installed in this container and I have no authority to install it. **This is an unrun test, not a pass.** The generator's `--check` (item 1) covers the same fidelity property as `test_the_committed_artifact_matches_the_generator`, and it passed; the other seven tests are **unverified by me**. I did not run `scripts/preflight.sh` (dispatch did not authorise it).

**PROPOSED (NOT RUN)** — the smallest correct cross-file invariant, offered for the owner's consideration, deliberately as a *reporting* check rather than a pooling rule, since the reading is theirs to choose:

```python
# PROPOSED (NOT RUN) — research/modalities/tests/test_emc_site_curation.py
def test_every_pooled_source_declares_its_registry_pool_flag():
    """Does not decide the reading. Requires only that a source the registry
    marks pool:false, which this file nevertheless pools, carries an explicit
    written justification key naming that divergence."""
    reg = json.load(open(REGISTRY))
    flags = {c["sourceId"]: c.get("pool") for c in reg["registry"]["cohorts"]}
    art = json.load(open(OUT))
    for block in art["pooled_extremity_fraction"].values():
        for sid in block["per_cohort_percent"]:
            if flags.get(sid) is False:
                assert any(sid in k for k in art["_method"]), sid
```

I have **not** run this, have **not** written it into the tree, and it is a suggestion only.

## Limitations

- **Transfer limit, load-bearing.** W13d's report does not exist at this HEAD or anywhere on the filesystem. Every W13d finding I relied on for framing — the fifth overlap-declaring row `treatments.systemicEvidence[7]`, the §2.3/§5 ruling that neither property is policy-required, the identification of this artifact as the single exposed one — is **taken from my dispatch prompt, not verified against a document**. I independently re-derived only the parts I needed: the `pool: false` flag, the `contextReason`, §2.3's text, and the exposure of this one artifact. I did **not** independently re-verify A5/A6 or the fifth row's existence beyond confirming `palmerini2022trobsultrarare` carries `pool: false, contextReason: population-overlap` in `.treatments.systemicEvidence[7]`.
- **HEAD ≠ the campaign's declared frozen commit.** I read `7d081218`, not `92abbcb9`. The four intervening commits appear to touch only campaign reports, but I did not diff them exhaustively against `research/modalities/` and the registry beyond observing their commit subjects.
- **`pytest` unavailable**: 7 of the 8 committed tests for this artifact are unverified by me. A skipped test is not a pass.
- **This is a decision-support package, not a decision.** I did not edit the registry, did not author a `populationKey` or a counterpart for any row, added no case to any denominator, corrected nothing, and endorsed neither figure. The committed figures (71.6% / 84.5% over 271) remain the committed figures.
- **No unit determination.** Every `n` here (41, 49, 59, 60, 134, 163, 171, 230, 271) is transcribed exactly as committed. I attach no reading of what any of them counts; that is W13c-resolved and W13b-owned.
- **No clinical claim.** Nothing here asserts efficacy, safety, selectivity or clinical readiness, and an "extremity fraction" states who a strategy could be *offered* to, not whether it would work — the file's own framing, preserved.
- **Absence claims are bounded.** "No committed field names a counterpart" is a statement about the tracked tree at `7d081218` and the frozen corpus's selected 5,996 files. Per `snapshot-provenance.json`, files absent from that snapshot are UNKNOWN, not absent from the repository. A counterpart could exist in an untracked or unretained record.
- **The `~1.2 pp` difference between readings is a measurement, not an argument.** I report it because the owner will want it; I do not offer it as a reason to prefer either reading.

## Stop condition

Set: *regeneration fidelity established; both readings computed side by side with the committed one identified; the counterpart question answered (named or UNKNOWN) from committed fields; consistency with W16b reported.*

**MET, all four.** (1) `--check` exit 0. (2) Both readings computed from the file's own estimator and interval, Reading A identified as committed, Reading B independently reproducing the file's retained superseded figures; neither endorsed. (3) Counterpart = **UNKNOWN** — no `populationKey` on `bishop2019`, no overlap-partner field anywhere in any tracked JSON, and the only committed statement is the hedged free-text `"likely within SEER / US Sarcoma Collaborative"` plus the generator quoting it back; no counterpart inferred from size, country, date, author or institution. (4) W16b **consistent** and complementary, with the composed observation recorded in §6.

One sub-goal fell short of full evidence: the artifact's 8-test module could not run (`pytest` absent). Recorded as BLOCKED, not as a pass.

## Tool-call and wall-clock count actually used

**24 tool calls** (all Bash; 3 issued as parallel pairs). **Wall clock ≈ 2 minutes** — `Tue Sep  8 02:34:57 UTC 2026` to `Tue Sep  8 02:36:56 UTC 2026`. Well inside the ~40-call / ~40-minute self-observed target; returned as soon as the stop condition was met, with no padding.

## Next concrete action

**One successor, and it is a decision request for the registry/policy owner, not computation:** ask the owner to resolve §2.3's silence on scope by choosing *one* of three, and to record the choice in `systems/POLICY-evidence.md` §2.3 so no future consumer has to invent it again —

(a) **per-source** (the exclusion travels; `emc-site-curation.json` reverts to its own retained 70.4 / 85.7 over 230, which requires no new number);
(b) **per-pool** (ratify the current committed 71.6 / 84.5 over 271, and add to §2.3 the sentence the generator currently supplies on policy's behalf);
(c) **per-pool but only against a named counterpart set** — which would require `bishop2019`'s row to gain a structured counterpart field, and that field's value is exactly the thing this report found to be **UNKNOWN**, so (c) is not actionable until someone with source access can name it.

Whichever is chosen, the second half of the action is the same and is independent of it: **something must read both files.** No gate, test or validator currently compares the site pool's membership to the registry's `pool` flags, so today's agreement or disagreement between them is unenforced either way. The proposed reporting-only test in the Validation section is the smallest version of that check and is offered unrun.

**Not for this lane**: naming the counterpart requires a source fetch against `ussc2022` (`doi:10.1002/jso.27062`, `oa_status: closed`, historically 403) — that is a source-access question under existing closure boundaries, not a bookkeeping one, and I did not attempt it.
