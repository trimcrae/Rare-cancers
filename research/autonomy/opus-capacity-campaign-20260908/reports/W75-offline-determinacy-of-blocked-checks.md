<!-- collected 2026-09-08T05:00:19Z by campaign coordinator; agent id ad04ab64d9434e45c; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ad04ab64d9434e45c.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W75** — offline-determinacy lane, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

- `date -u` **start** `Tue Sep  8 04:54:24 UTC 2026` · **end** `Tue Sep  8 04:57:29 UTC 2026`
- `git rev-parse HEAD` **start** `fcb36d3c651223d90b98c0cb64169bb106e6e060` · **end** `129a4e2a1c39352a7a697c42445bb27fc50f9b0c` (coordinator landing sibling reports under me).
- `git status --porcelain` **start** and **end**: no entry outside `research/autonomy/opus-capacity-campaign-20260908/` at either point (filtered check run at end returned zero lines). I ran no git write operation, wrote nothing into the repository, executed no module, and made no network call of any kind. Scratch `/tmp/claude-0/w75/` created and **deleted** (`rm -rf`; `ls` confirms absent).
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start):

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
GLOBAL_AGENT_NO_PROXY=<same no_proxy list>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<truststore/proxy flags only>
NO_PROXY=<same list>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same list>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**No variable names a model.** Also measured: `TRANSCRIPT_SOURCE` is **UNSET** in this environment (`echo "TRANSCRIPT_SOURCE=[${TRANSCRIPT_SOURCE:-UNSET}]"` → `TRANSCRIPT_SOURCE=[UNSET]`) — this is load-bearing for R2/R3 below.

## Question

For W34c's three honestly-UNKNOWN `--check` gates — `research/modalities/aso_noncoding_acceptor_designs.py:1181`, `research/modalities/pgr_parent_engagement.py:230`, and the AFND half of `research/modalities/hla_coverage.py:426` — **what does fetched data actually contribute to the verdict, and what fraction of each check is determinate offline?** Per module: (a) what a green offline run establishes and does not; (b) whether "fetch failed" is distinguishable from "check passed" in exit code and in output text; (c) whether a committed cache would let the fetch-dependent assertions run offline.

Open because W34c's blocked-egress result is a measurement of the environment, not of the modules, and nobody has read the three check paths line by line.

## Prior-work check

Read in full first, as dispatched: `COMMON-BRIEF.md` (including the whole "Known, measured, and NOT worth rediscovering" section), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W34c-lossy-remediation-advice-census.md`. W34c's **31 green / 4 red / 3 UNKNOWN** split is taken as given and not re-measured.

Search commands run on the live tree:

```
git ls-files | grep -i -E "afnd|allelefreq|iso-3166|iso3166|hla"
grep -rn "TRANSCRIPT_SOURCE" --include=*.py --include=*.sh --include=*.yml -l . | grep -v opus-capacity
```

The first returns 5 paths (`S29-HLA-STALE.md`, `hla-coverage-emc.md`, `hla-coverage.json`, `hla_coverage.py`, `tests/test_hla_coverage_seam_provenance.py`) and **no committed AFND or ISO cache file**. The second returns 18 files, and is the basis of R2/R3.

Adjacent campaign work confirmed to be a different axis, not a duplicate: **W34c** = classification of the advised remedy (SAFE/LOSSY), which left these three unclassified; **W45** = whether regeneration-then-check escapes a gate; **W27** = what a `--check` compares in general. None reads these three check paths. **`reports/W25-*` was not read or referenced.** Nothing from `CLOSED-WORK.md` was replayed: no NR4A Perspective, no denied publisher route, no GSE re-read, no registry work, no publication act. No content-policy refusal occurred. **No network call of any kind was attempted, and none of the three modules was executed.**

## Method and inputs

Pure source reading plus reading of committed JSON artifacts, in the live checkout `/home/user/Rare-cancers` at HEAD `fcb36d3c` → `129a4e2a`. Files read:

- `research/modalities/hla_coverage.py` (559 lines) — `fetch()` `:73-82`, `load_afnd()` `:140-207`, `class_ii_seam_grade` `:303-316`, `check()` `:366-437`, `main()` `:437-559`.
- `research/modalities/pgr_parent_engagement.py` (251 lines) — whole file; `build()` `:124-221`, `main()` `:223-247`.
- `research/modalities/aso_noncoding_acceptor_designs.py` (1204 lines) — `_parents()` `:559-569`, `build()` call sites `:562,660,783,796-797,942`, `main()` tail `:1176-1200`.
- `research/modalities/junction_aso.py` — `TRANSCRIPT_SOURCE` `:274`, `_model_from_committed_cache` `:309-345`, `_diff_live_against_cache` `:384-396`, `transcript_model` `:401-443`, `transcript_source_provenance` `:446-459`.
- Committed artifacts, read with `json.load` only: `hla-coverage.json`, `pgr-parent-engagement-noncoding-acceptor.json`, `aso-noncoding-acceptor-designs.json`, `emc-construct-inputs.json`.

Python 3.11.15 (`/usr/local/bin/python3`) used **only** to load and count JSON leaves of committed artifacts. **Every verdict about module behaviour below is SOURCE-DERIVED, not an executed result.**

## Result

### R1 — The three are not one phenomenon. They split 1 + 2. (PRIMARY, source-derived)

`hla_coverage.py --check` and the other two have **opposite architectures**:

| | `hla_coverage.py` | `pgr_parent_engagement.py` · `aso_noncoding_acceptor_designs.py` |
|---|---|---|
| Check shape | a **bespoke offline invariant check** over the committed artifact (`check()`, `:366`), dispatched *first* in `main()` (`:437-438`, `sys.exit(check())`) so the producer is never entered | **regenerate-and-byte-compare**: `art = build()` runs **before** the `--check` branch (`pgr:225`, `aso_noncoding:1176`), so the check inherits every input dependency of the producer |
| Network in the check path | **none** — `check()` opens `OUT` and `CD4_DEMO` only; `fetch()` is unreachable from it | `build()` → `ja.transcript_model()`, which under `auto` attempts an Ensembl REST read |
| Fraction of the artifact compared | **2 of 448 leaves** (`_class_ii_note`, `global.class_ii_cd4_helper_alleles`) ≈ 0.4% | **100%** of the serialized artifact, byte-for-byte (148 leaves for pgr, 857 for aso_noncoding) |

### R2 — ⭐ The two "blocked-egress" reds are determinate offline, and the fetch is not what makes them red (PRIMARY, source-derived)

`junction_aso.py:274` reads `TRANSCRIPT_SOURCE = os.environ.get("TRANSCRIPT_SOURCE", "auto")` **at import time**, and `transcript_source_provenance()` (`:448`) emits that literal string as `{"requested": TRANSCRIPT_SOURCE, ...}` into the artifact. Both committed artifacts record:

```
"transcript_source": { "requested": "cache",
                       "used_per_gene": { EWSR1 … NR4A3 : "committed_cache" (7/7) },
                       "committed_cache_fetched_utc": "2026-08-12T13:41:57Z", … }
```

Neither module pins the source. `hla_coverage.py:311` does (`os.environ.setdefault("TRANSCRIPT_SOURCE", "cache")` before importing `junction_aso`); `pgr_parent_engagement.py` never mentions the variable, and the only `TRANSCRIPT_SOURCE` occurrence in `aso_noncoding_acceptor_designs.py` is `:187`, inside a **prose evidence string**, not a `setdefault`. `TRANSCRIPT_SOURCE` is unset in this container (measured above).

**Consequence, source-derived:** a bare `python3 <module> --check` regenerates with `requested = "auto"`, which cannot equal the committed `"cache"`. The byte compare fails **before the network is relevant at all**. So:

- W34c's `403` line for these two is not a fatal error. `transcript_model:430-437` scopes the fallback to the fetch: on any exception under `auto` it prints `Ensembl unreachable for {symbol} ({exc}); using the committed cache` — which is where the `<urlopen error Tunnel connection failed: 403 Forbidden>` text came from — and continues on the cache. The `rc 1` came from the byte compare, whose message is `… is stale; re-run without --check`.
- ⛔ **These two are RED under the default environment on a networked runner too, and for a *different* reason.** With Ensembl reachable, `used_per_gene` becomes `"ensembl"`/`"ensembl+cache_agreed"` (`:439`) instead of the committed `"committed_cache"`, and `requested` is still `"auto"` — two provenance mismatches instead of one. And if live annotation has drifted, `_diff_live_against_cache:390-395` **raises** rather than falling back. **W34c's proposed remedy — re-run these two on a networked Actions runner — cannot produce a green**, so it would not resolve the UNKNOWN it was proposed for. The invocation that could is `TRANSCRIPT_SOURCE=cache python3 … --check`, which by `:422-423` provably never touches the network. **I did not run it** (dispatch: do not run a module that attempts egress under the invocation read), so whether the remaining leaves agree is **UNKNOWN**.
- **Fraction determinate offline:** for both modules the *scientific* content of the check is **100% offline-derivable from committed bytes** — `emc-construct-inputs.json` carries all 7 partner genes with the four required `self_checks` (`:331-341`), and both committed artifacts record 7/7 `committed_cache`. The **only** fetch-sensitive leaves are inside the 10-leaf provenance block (`requested`, 7× `used_per_gene`, `committed_cache_fetched_utc`, `_caveat`) — **10 of 148 leaves (6.8%) for pgr and 10 of 857 (1.2%) for aso_noncoding** — and of those, one (`requested`) is a pure function of the invoking environment, not of any fetch.

### R3 — Per-module answers to (a), (b), (c) (PRIMARY, source-derived)

| | `aso_noncoding_acceptor_designs.py:1181` | `pgr_parent_engagement.py:230` | `hla_coverage.py:426` |
|---|---|---|---|
| **(a) a green establishes** | that all 857 leaves — designs, seams, gap-specificity margins, the parent-exclusion screen over 7 transcripts — regenerate byte-identically from committed inputs. Green is **not currently attainable** with a bare invocation (R2). | that all 148 leaves regenerate byte-identically, including `headline_pgr` (5 designs, 0 near-matches ≤2 mm in wild-type PGR). Same non-attainability. | **only** that `_class_ii_note`'s stated count equals the allele list printed beside it, that that list equals `patient-cd4-demo.json`'s `patient_class2_hla`, and that `global.class_ii_cd4_helper_alleles` equals the strong calls on disk. |
| **(a) a green does NOT establish** | that any transcript model matches Ensembl today (the cache is dated `2026-08-12T13:41:57Z`); the provenance block agreeing is compatible with the annotation having drifted, since nothing was fetched. | same. Note the artifact's own `⚠_what_a_zero_here_does_and_does_not_mean` already scopes the scientific reading; nothing here bears on it. | **anything at all about the AFND frequency figures, the Wilson CIs, the 16 regional tables, or the coverage numbers** — 446 of 448 leaves are outside the check. The check would be equally green over an artifact whose entire frequency arm read `source_unavailable`. |
| **(b) distinguishes fetch-failure from pass?** | **Exit code: NO.** A fetch failure is swallowed by `transcript_model:432-437` (or, deeper, by `_parents():566-570` and the `build()` try/except at `:795`), and the process exits 1 only via the generic byte compare. **Output text: PARTIALLY.** The fallback line and `⚠ parent {sym} unavailable` go to stderr, and unloadable seams surface as `junctions_not_buildable_in_this_environment` — but the **verdict line is the boilerplate `… is stale; re-run without --check`**, which names a staleness that may be an environment difference. | **Exit code: NO** (identical mechanism). **Output text: PARTIALLY** — the same stderr fallback line appears, the verdict line is the same boilerplate `pgr-parent-engagement-noncoding-acceptor.json is stale; re-run without --check`. | **Not applicable in the exit code — there is no fetch in the check path.** **Output text: YES, explicitly**, and this is the module's designed behaviour: the exit-0 line reads `hla-coverage.json: class-II panel note and helper set agree with patient-cd4-demo.json (⚠ the AFND frequency figures are NOT checked here -- that needs the fetch)`. Its docstring `:368-386` states the design rationale verbatim: *"a gate that claims to guard the expensive half without fetching it would be"* weaker. |
| **(c) would a committed cache let the fetch-dependent assertions run offline?** | **YES, and it already exists and is already in use.** `emc-construct-inputs.json` + `TRANSCRIPT_SOURCE=cache`. Nothing needs adding; the gap is that the invocation is not pinned. | **YES, same cache, same gap.** | **NO.** `git ls-files` finds **no committed AFND or ISO artifact**. `fetch():73-82` returns `""` after 4 retries; `load_afnd:154` then sets `source_ok = False`; `main:478` sets `regions = {}` and `:491-494` stamps `_source_status: "UNAVAILABLE: AFND mirror TSV not retrievable; coverage NOT computed rather than fabricated"`. Honest, but not offline-runnable. |

### R4 — ⛔ One consequence of R3 the owner should see (PRIMARY, source-derived)

`hla_coverage.py`'s advised remedy at `:426` — `⛔ regenerate with python3 research/modalities/hla_coverage.py` — has **no `source_ok` guard on the write**. The write at `:544-546` is unconditional. Run offline, it would replace the committed 448-leaf artifact with one whose 16 regional tables are `{}` and whose per-allele frequencies are `source_unavailable`, overwriting a dated measurement — and **`--check` would still exit 0 afterwards**, because the two fields it reads are derived from `patient-cd4-demo.json` and are invariant to the entire AFND arm. This is not a fabrication risk (the artifact would label itself `UNAVAILABLE`), and it is not the destructive class W34c identified for `aso_control_oligos.py` (no hand-applied correction is at stake). It is a **loss-of-measurement-under-a-green-gate** risk, and it is the same failure shape the module's own docstring records for 2026-08-28. I authored no repair and propose none here.

### R5 — Direct answer

**The fetched data contributes nothing to any of the three verdicts today.** For `hla_coverage.py` the fetch is architecturally excluded from the check and the module says so in its own output; the check is **0.4% of the artifact by leaf count and 100% determinate offline** within that scope. For the other two the check is a full-artifact byte compare that is **100% determinate offline given `TRANSCRIPT_SOURCE=cache`** — the committed cache covers all 7 genes — and their reds are caused by an **unpinned provenance string**, not by the 403. W34c's UNKNOWN classification was the right call on the evidence it had; the correct refinement is that two of the three are **decidable without any network** and the third **cannot be made green by a network either**.

## Validation evidence

**Environment**: Linux 6.18.44-fc-v24 x86_64, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Python 3.11.15. `scripts/preflight.sh` **not** run. `atr_hrd_sarcoma_series.py` **never invoked**. No `--refresh`/`--fetch` mode run. **No module under study was executed. No network call was attempted.**

**RUN — read-only, exit 0 each**, cwd `/home/user/Rare-cancers`:
```
echo "TRANSCRIPT_SOURCE=[${TRANSCRIPT_SOURCE:-UNSET}]"        → TRANSCRIPT_SOURCE=[UNSET]
git ls-files | grep -i -E "afnd|allelefreq|iso-3166|iso3166|hla"   → 5 paths, no AFND/ISO cache
grep -rn "TRANSCRIPT_SOURCE" --include=*.py --include=*.sh --include=*.yml -l . | grep -v opus-capacity  → 18 files
python3 -c "json.load(...); leaf count"  → hla-coverage.json 448 leaves;
                                            pgr-parent-engagement-noncoding-acceptor.json 148 (provenance block 10);
                                            aso-noncoding-acceptor-designs.json 857 (provenance block 10)
```
Verbatim committed provenance, both modules: `"requested": "cache"`, 7/7 `"committed_cache"`, `"committed_cache_fetched_utc": "2026-08-12T13:41:57Z"`.
Verbatim `hla_coverage.py` green line (source, `:432-435`): `hla-coverage.json: class-II panel note and helper set agree with patient-cd4-demo.json (⚠ the AFND frequency figures are NOT checked here -- that needs the fetch)`.

**SOURCE-DERIVED, NOT EXECUTED** (label binding on every row of R2/R3/R4): every statement about what a run would print, return, write or fetch. I read the branches; I did not run them.

**PROPOSED (NOT RUN)**: `TRANSCRIPT_SOURCE=cache python3 research/modalities/pgr_parent_engagement.py --check` and the same for `aso_noncoding_acceptor_designs.py`, in a scratch copy — provably offline by `junction_aso.py:422-423`, and the one invocation that could turn either UNKNOWN into a measured green or a real content diff. Not run here: my dispatch forbade running a module I had read as attempting egress, and the pin was only established mid-read.

## Limitations

- Everything here is a reading of source, not a run. A module can diverge from its branches at runtime; the R2 prediction that `requested: "auto" ≠ "cache"` forces inequality is a strong inference but remains **unexecuted**.
- I established that the provenance mismatch is **sufficient** to make the two checks red. I did **not** establish it is the **only** difference — whether the other 138 / 847 leaves also differ is **UNKNOWN** and needs the pinned-cache run above.
- Whether Ensembl's current annotation agrees with the `2026-08-12` cache is **UNKNOWN** and deliberately unmeasured. A cache is not a measurement of today; `junction_aso.py:268-272` says so itself.
- Leaf counts are a size proxy, not an importance measure. The 2/448 that `hla_coverage.py --check` reads are precisely the two fields whose disagreement caused the 2026-08-28 defect, so a small fraction is not the same as a weak check.
- **Nothing here is a scientific result.** No claim is made or implied about EMC biology, ASO efficacy, safety, selectivity, coverage, therapeutic window or clinical readiness; allele frequencies, transcript models and design screens appear only as inputs to a file-freshness comparison. No screen's content is restated as a finding. There is no wet lab.
- I authored no repair, patch, gate, test or cache; weakened, relaxed and reordered no guard; ran no advised writing command; and attempted no retrieval or route around the recorded denial.

## Stop condition

Set up front: **stop once each of the three `--check` paths has been read line by line, each assertion classified as network-dependent or committed-bytes-only, and (a)/(b)/(c) answered per module.** **MET.** All three read; the fetch-dependent surface is quantified at 10/148, 10/857 and 0/448 leaves respectively; all nine sub-answers given. Returning early against the ~40-call target.

## Tool-call and wall-clock count actually used

**21 tool calls; 3 min 05 s wall clock** (04:54:24Z → 04:57:29Z).

## Next concrete action

**One finite, safely-executable successor**, for a worker with the same read-only posture: run `TRANSCRIPT_SOURCE=cache python3 research/modalities/pgr_parent_engagement.py --check` and the same for `aso_noncoding_acceptor_designs.py` in a scratch copy — provably offline by `junction_aso.py:422-423` — and report the exit code plus, if still red, the leaf-level diff. That converts two of W34c's three UNKNOWNs into measured results with no network and no repair. It should be dispatched with the explicit finding that **a networked Actions runner is the wrong instrument for these two** (R2), so W34c's proposed CI resolution should be retired rather than queued. The `hla_coverage.py` AFND half stays **UNKNOWN by construction** and cannot be resolved by any offline run; R4 is a routing note for the neoantigen-artifact owner, not a task for a worker.
