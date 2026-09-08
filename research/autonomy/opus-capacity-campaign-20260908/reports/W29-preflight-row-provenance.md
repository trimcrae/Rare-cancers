<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:23:21Z UTC
     agent id a0787f93df69ee892 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a0787f93df69ee892.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

## Worker

**W29** — preflight-gate provenance lane, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in my environment independently confirms a served model.

`date -u` **start**: `Tue Sep  8 03:14:07 UTC 2026` · **end**: `Tue Sep  8 03:19:54 UTC 2026`

`git rev-parse HEAD` **start**: `98a0833f1ede2cf9cef13790388260567a32e868` · **end**: `84f02dae1809ae050e40254f06310ed849982527`. HEAD moved under me (coordinator report collection). `git status --porcelain` **start**: 8 untracked files, all `research/autonomy/opus-capacity-campaign-20260908/reports/W*.md` (W01g, W02f, W04e, W06f, W07f, W09f, W12e, W20g); **end**: **empty** — those files were committed by the coordinator, which is exactly the delta between the two HEADs. **No file I measured** (`scripts/preflight.sh`, any of the 18 modules, any artifact) is in that delta. I wrote nothing into `/home/user/Rare-cancers` and ran no git write operation. All execution was under `/tmp/claude-0/w29/` with `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w29/pyc`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; the four long proxy-list variables `GLOBAL_AGENT_NO_PROXY`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` are elided only where they repeat the `no_proxy` value verbatim):

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
GLOBAL_AGENT_NO_PROXY=<same list as no_proxy>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<proxy/truststore flags; repeats the no_proxy list>
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

## Question

For each of the 18 `--check` rows of the re-derivation gate in `scripts/preflight.sh`: **what does the row's `--check` actually assert, read from the module's source rather than inferred from its row label; is that assertion against committed bytes, a recomputation, an external fetch, or nothing beyond a parse; does the module write anything while `--check` runs; and can the assertion pass vacuously?** Then: how many of the 18 would still exit 0 against an empty or trivially-degenerate input, and does any row exit 0 only because a network fetch was denied?

Open because several campaign reports (W12c, W12d, W12e) now carry per-row denominators — "16 of the 18 gate rows", "18/18 byte-identical", "all 18 rc=0" — that treat the 18 as a uniform population of read-only re-derivations, which is also what `scripts/preflight.sh`'s own inline comment asserts. Nobody has read the 18 `--check` bodies and classified them.

## Prior-work check

Read in full as instructed: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, and `reports/W13f-cross-file-gate-coverage.md`. W12c, W12d, W12e and W17h were read via targeted extraction (`grep -n -i -E "preflight|--check|845|vacuous|18 row|eighteen"` over each, then the matched passages in context) rather than end to end.

What the prior reports established, and where my unit is disjoint from theirs:

- **W12c** (`reports/W12c-stdout-defect-census.md:161`) enumerates the 18 rows as a *list of file paths* and counts non-ASCII `print` sites inside them (52 sites, 16 of 18 rows). It states explicitly at its line 312: "I applied **no repair**, ran **no generator**, and ran **no `--check`**", and at line 314 that it "did **not** verify that each listed print site is actually on the `--check` code path". It never reads a `--check` body.
- **W12d** ran all 18 rows and recorded exit codes and stdout digests under three locales (its §3, lines 198–200). That is *behaviour under a locale perturbation on unmodified input*; it makes no claim about what any row asserts. Its line 288 is the explicit gap I am filling: "The `--check` rows are read-only *by design and by the gate's own documented contract*; I verified this empirically only through `git status`, which is a whole-tree assertion, not a per-row one."
- **W12e** measured subprocess environment inheritance; no per-row semantics.
- **W17h** is a Welch-coverage census, unrelated.
- **W13f** measured cross-file `pool`-flag enforcement over registry consumers; its subject is `scripts/validate-registry.mjs` (preflight gate 10), not the re-derivation gate. My lane does not touch the registry, pooling, or any clinical artifact.

Concurrent siblings W27 (drift-gate key coverage) and W13g (cross-file gate holes) are not duplicated: I read no drift-gate key list and measured no cross-file hole. My unit is the 18 rows' own `--check` code.

**Correction to a shared citation.** The dispatch names `scripts/preflight.sh:845-866` and W12c names `849-866`. Neither is the row list. `845` is `_genout="$(mktemp -d)"`; `866` is a comment inside the loop body. **The 18 row literals are `scripts/preflight.sh:847-864`**, verified by `grep -n '|--check' scripts/preflight.sh` returning exactly 18 lines, 847 through 864.

CLOSED-WORK items confirmed not replayed: no PUB-EMC-CLASSIFICATION, no Brenca/Hofvander/Davis, no `GSE4303`/`GSE28866` analysis, no NR4A Perspective, no source fetch, no clinical claim.

## Method and inputs

| Input | Path | Role |
|---|---|---|
| The gate | `/home/user/Rare-cancers/scripts/preflight.sh:840-910` | row list (847–864) + fan-out and reporting loop |
| 18 modules | the paths in the table below | `--check` bodies read in source |
| Scratch tree | `/tmp/claude-0/w29/tree` | `tar`-copy of the working tree **without `.git`** (611 MB, 7,814 files) — the only place any degenerate input was created |
| Live tree | `/home/user/Rare-cancers` | two rows executed here read-only after source inspection proved their `--check` branch returns before any write; `git status --porcelain` compared before and after |

`python3` is the system interpreter. No `pytest`. `scripts/preflight.sh` was **not run**. No paid API, no GPU, no publication.

## Result

### R1 — Per-row provenance table (`PRIMARY`, from source)

Row numbers are 1-based over `scripts/preflight.sh:847-864`. "Assertion" is read from the module's `--check` branch, not from the row label.

| # | Line | Module · mode | What `--check` actually asserts | Class | Writes on `--check`? | Vacuous pass reachable? |
|---|---|---|---|---|---|---|
| 1 | 847 | `research/manuscripts/submission_tables.py` `--check` | Rebuilds the whole `-submission-tables.md` document in memory; `have == doc` byte compare against the committed file; missing file → rc 1 | **committed bytes vs recomputation** | no | **no** |
| 2 | 848 | `research/manuscripts/claim_coverage.py` `--check` | `build_report()` runs the live census, then `disagreements()` compares **field-by-field in both directions** against the committed JSON, plus a byte backstop; a document present in the artifact but no longer censused is named explicitly ("its numbers are a reading of nothing"); missing artifact → rc 1; `--write --check` together → rc 2 with the reason; unknown flag → rc 2 | **committed bytes vs recomputation** | no | **no** |
| 3 | 849 | `research/manuscripts/submission_citations.py` `--check` | Compares the superscripts **printed** in the manuscript against the numbering **derived** from the PMID comments in that same file. Self-consistency of one committed file. It does **not** compare against the `.md`/`.json` outputs `--write` produces | recomputation vs **the same file's other half** | no | **YES** (empty collection) |
| 4 | 850 | `research/manuscripts/submission_metrics.py` `--check` | Recomputes every word/figure count, `have == doc` byte compare; missing → rc 1. The one `except Exception` is inside the **failure-rendering** path only (`hv = {}`), after rc 1 is already decided | **committed bytes vs recomputation** | no | **no** |
| 5 | 851 | `research/manuscripts/aso_sequence_manifest.py` `--check` | Two byte compares (`OUT_CSV`, `OUT_FASTA`); **plus** a coverage assertion that runs *before* either mode — every sequence named in the deposit documents must be a manifest row, else rc 1 | **committed bytes vs recomputation** + a set containment | no | **no** |
| 6 | 852 | `research/manuscripts/aso_journal_tables.py` `--check` | `current != text` byte compare; missing → rc 1 | **committed bytes vs recomputation** | no | **no** |
| 7 | 853 | `research/modalities/aso_offtarget_duplex_energy.py` `--check` | Rebuilds the duplex-energy artifact and compares the JSON with the `parameters` key dropped (package version legitimately varies); missing → rc 1; **Biopython absent → REFUSED, rc 1** (fails closed rather than skipping) | recomputation vs committed JSON (one key excluded, announced) | no | **no** |
| 8 | 854 | `research/manuscripts/submission_packet.py` `--check` | Rebuilds `SUBMISSION-PACKET.md` and byte compares; missing → rc 1 | **committed bytes vs recomputation** | no | **no** |
| 9 | 855 | `research/manuscripts/vaccine_path_tables.py` `--check` | Splices freshly built blocks into the committed manuscript text and compares the whole file; a missing `BEGIN`/`END` sentinel raises `SystemExit` → rc 1 | **committed bytes vs recomputation** | no | **no** |
| 10 | 856 | `research/manuscripts/aso_archive_manifest.py` `--check-archive` | **Provenance first**: reads the *on-disk* manifest's clean-tree flag and refuses on `false` / `null` / missing (rc 1). Then rebuilds the inventory — `{path, bytes, sha256}` for every promised file — and compares the archive-only projection. Missing manifest → rc 1; unreadable JSON → rc 1. `_archive_only` deliberately drops repository-state fields; that narrowing is documented, not silent | **recomputed sha256 of committed bytes** | no | **no** |
| 11 | 857 | `research/manuscripts/aso_deposit_drift.py` `--check` | Compares the committed generated block against a freshly measured one. The measurement is `git show <published rev>:<manifest>` vs the manifest **on disk**. `_digests_at` returns `None`, never `{}`, when the rev is unreadable — deliberately, so absence never renders as "deposited nothing" | recomputation, **git-object read**, **network-capable** (see R3) | no | **YES, announced** |
| 12 | 858 | `research/modalities/emc_condensate_report.py` `--check` | Renders the findings note and byte compares; missing → rc 1 | **committed bytes vs recomputation** | no | **no** |
| 13 | 859 | `research/modalities/atr_hrd_sarcoma_series.py` `--check` | Offline. Three independent assertions: (a) `single_slot_identity.check_slot` binding, failing closed if no slot names this producer; (b) two SERIES MISMATCH guards, one on the cache and one on the committed artifact; (c) `derive()` from the committed inputs cache, JSON-equality against the committed artifact | recomputation vs committed JSON + identity binding | **YES — see R4** | **no** |
| 14 | 860 | `research/modalities/single_slot_identity.py` `--check` | Iterates a hard-coded `SLOTS` registry, binding each artifact's declared identity across artifact, caches, systems map and declaring documents. **Explicitly refuses an empty registry**: `print("REGISTRY EMPTY — this guard measured nothing"); return 1` | validation of committed data | no | **no — the only row that names and closes this hole** |
| 15 | 861 | `research/modalities/instrument_census.py` `--check` | Rebuilds the census from the roadmap markdown and byte compares **both** committed copies (`.json` and `.md`); either missing → rc 1 | **committed bytes vs recomputation** | no | **no** |
| 16 | 862 | `scripts/trigger_scan.py` `--check` | Validates hand-written trigger rows against route/blocker ids in `systems/graph/` and `emc-systems-map.json`, plus `cite_into` path existence and a reverse join | **validation, nothing recomputed** | no | **YES ×2** |
| 17 | 863 | `scripts/citation_debt.py` `--check` | For each ledger row, checks the destination file exists, is text, and that a `discharged` status has its PMID/DOI actually present in the bytes | **validation, nothing recomputed** | no | **YES** |
| 18 | 864 | `scripts/news_match.py` `--check` | Validates the committed match queue: `_model` present, statuses in range, every `publication_id` resolves in `systems/graph/publications.json`, no empty reasons | **validation, nothing recomputed** | no | **YES** |

### R2 — Vacuous-pass surface: **5 of 18 rows (28 %)** (`PRIMARY`)

A row is counted vacuous when there is a reachable `rc = 0` that asserts nothing beyond a successful parse.

| Row | Module | The vacuous path, quoted from source | Demonstrated? |
|---|---|---|---|
| 18 | `news_match.py` | `if not os.path.exists(QUEUE): print("news_match --check: no queue committed yet — nothing to validate"); return 0`, and `for n, row in enumerate(q.get("items", []))` over an empty list | **YES — D1, rc 0** |
| 17 | `citation_debt.py` | `for row in led.get("rows", [])` — an empty `rows` yields no errors and prints "every declared destination is decided and every discharge verified". Separately, `if trg and trigger_ids and trg not in trigger_ids` silently disables the trigger-pointer join whenever `research/method-watch-triggers.json` is unreadable | **YES — D2, rc 0** |
| 16 | `trigger_scan.py` | (a) `if not os.path.exists(REGISTRY): print("… skipping cross-check"); return 0`; (b) `for t in cfg["triggers"]` over an empty list → "0 ERROR across 0 trigger(s)" | **YES — D3 and D5b, both rc 0** |
| 11 | `aso_deposit_drift.py` | When the published revision cannot be resolved, `render()` emits an "⚠ The drift cannot be measured here … UNKNOWN, which is not the same as zero" block. If that is the block that is committed, the freshly rendered block equals it and `--check` exits 0 having measured no drift | **YES — D6, rc 0** |
| 3 | `submission_citations.py` | `--check` only iterates `cites` (annotated superscripts) and `bare`; both empty → "citation numbering is current", rc 0. Separately, the fetched-record half is **not gated at all**: records unreachable on `origin/literature-cache` land in `without_fetched_metadata` and `--check` still returns 0 | **no — source-derived only** |

**The remaining 13 rows cannot pass on a degenerate input, and the reason is structural.** They re-derive their artifact in-process and compare it to the committed bytes. Emptying the *input* changes the *recomputation*, so the comparison against the unchanged committed artifact goes red rather than green. The 5 vacuous rows are exactly the 5 that **validate hand-written data** instead of re-deriving a generated artifact — the vacuous surface tracks the row's kind, not its author's care.

**Two rows deserve explicit credit against the campaign's working assumption.** `single_slot_identity.py` (row 14) is the only module in the repository I found that names the empty-collection defect and fails on it — `"REGISTRY EMPTY — this guard measured nothing"`, rc 1. And `claim_coverage.py` (row 2) refuses `--write --check` together with the reason ("the write would produce the reference the check then reads"), rejects unknown flags with rc 2, and `disagreements()` compares in both directions so a document silently dropped from the census is reported rather than passing. Row 10's provenance gate runs *before* `build()` and refuses a manifest whose clean-tree flag is `null` or missing, not merely `false`. **On the specific question of comparing against a value the same run just produced, the gate is more rigorous than the campaign's reports assume — three of the 18 rows carry named, working defences against exactly that.**

### R3 — Network: **0 of 18 `--check` paths make an HTTP request** (`PRIMARY`)

| Fact | Evidence |
|---|---|
| `urllib`/`requests` appear in only 2 of the 18 modules | `atr_hrd_sarcoma_series.py` (4 `urlopen` sites), `trigger_scan.py` (4). In both, every site is on a path `--check` does not take: `--fetch`/`--fetch-quant` for the first (`--check` is documented and implemented as "offline: re-derive from the inputs cache"), the scan mode for the second (`--check` dispatches to `check_registry` before any query) |
| The only network-capable `--check` is row 11 | `aso_deposit_drift.measure()` calls `_git(["fetch", "--quiet", "origin", rev])` when the published revision is not resolvable locally — a **git transport**, not a publisher HTTP fetch |
| It is **not** exercised on this checkout | published `git_revision` = `4fd4698daec0c39ac77544083dc35d053a4e1e7e`; `git cat-file -e 4fd4698…` → **PRESENT locally**, so the fetch branch is never entered |
| The proxy **denies** the hosts the non-`--check` paths use | `curl https://eutils.ncbi.nlm.nih.gov/…` → `curl: (56) CONNECT tunnel failed, response 403`; `curl https://www.ebi.ac.uk/europepmc/…` → same. `$HTTPS_PROXY/__agentproxy/status` lists these as `connect_rejected`, `"gateway answered 403 to CONNECT (policy denial or upstream failure)"`. **Recorded as denied routes; not retried, not rerouted, not rephrased.** |
| The proxy **permits** git to origin | `git ls-remote --exit-code origin HEAD` → `92abbcb905cacf07f14b238db50d1b98f6590374`, rc 0 |

**Therefore no row of this gate exits 0 because its fetch was denied.** The two denied hosts are unreachable from any `--check` path, and the one network-capable row uses a transport this container allows and does not need on this checkout. This is a negative result and it is worth stating plainly: the concern the dispatch raised does not apply to these 18 rows here.

The two rows that *do* shell out are reading **local git objects**: `submission_citations.py` runs `git ls-tree -r --name-only origin/literature-cache` and `git show origin/literature-cache:<path>`, and `aso_archive_manifest.py` runs `git` with a 20 s timeout. A missing `origin/literature-cache` degrades row 3's metadata half silently (see R2) — but that is an ungated-assertion defect, not a denied fetch.

### R4 — `scripts/preflight.sh`'s own comment is wrong about one row (`PRIMARY`)

`scripts/preflight.sh:869-871` asserts, of all 18: *"Every row is an independent read-only `--check` against the committed tree — none writes"*, and again at line ~886: *"a `--check` that wrote the tree would already be failing `git_tree_is_clean_apart_from_this_manifest`."*

**On the current inputs this holds — I measured it.** A file manifest (`path size mtime`) over all 7,814 files of the scratch tree, taken before and after running all 18 rows, is **byte-identical**: `diff before.txt after.txt` → `NO CHANGE`.

**But row 13 writes when its artifact is absent.** `atr_hrd_sarcoma_series.py`, in the `--check` fall-through:

```python
if not os.path.exists(art_path):
    with open(art_path, "w") as f:
        json.dump(fresh, f, indent=1, sort_keys=True)
    print("artifact written from the cache")
    return rc
```

Demonstrated (D4b): with `research/modalities/atr-hrd-sarcoma-series.json` deleted, `--check` **re-created the file** (sha256 `d469cb27c8e5…`, identical to the deleted one) and printed `artifact written from the cache`. The row still exits **1**, because the `single_slot_identity` binding fires first on the missing artifact and sets `rc = 1` — the module's own comment says this door was found and closed on 2026-08-27. So: **the write is real and the preflight comment is inaccurate; the vacuous *pass* it once produced has been closed.** Both halves matter, and only one of them is fixed.

## Validation evidence

Environment for every run below: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, system `python3`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w29/pyc`, cwd `/tmp/claude-0/w29/tree` unless stated. No network except the three probes in R3.

**RUN — baseline, unmodified scratch copy** (`cd /tmp/claude-0/w29/tree; python3 <module> --check`):

```
news_match      rc=0   news_match --check: 0 ERROR across 47 queued item(s); …
citation_debt   rc=0   citation debt: 4 record(s), 12 destination(s) / every declared destination is decided
trigger_scan    rc=0   trigger_scan --check: 0 ERROR across 39 trigger(s); 27 registry revival_trigger field(s) seen
atr_hrd_…       rc=0   OK — the slot is bound to GSE299349 … / OK — the artifact re-derives byte-identically
```

**RUN — all 18 rows on the scratch copy, with tree delta.** 16 rc 0; rows 9 and 10 rc 1 (`STALE: the archive inventory would change`; `the declared deposit drift is not the measured one`) — **because the scratch copy has no `.git`**, so both fail closed rather than skipping. Tree manifest before vs after over 7,814 files: `NO CHANGE`.

**RUN — rows 9 and 10 in the live tree**, executed only after source inspection established that both `--check` branches `return` before any `open(..., "w")` and that row 10's git-fetch branch is unreachable here (R3):

```
$ python3 research/manuscripts/aso_archive_manifest.py --check-archive
manifest inventory is current (repository-state fields not compared)
rc=0
$ python3 research/manuscripts/aso_deposit_drift.py --check
rc=0
$ diff gs_before.txt gs_after.txt   →   NO TREE CHANGE
```

**So all 18 rows are green at the live HEAD.** The scratch reds are an artifact of the absent `.git` and are themselves evidence of fail-closed behaviour.

**RUN — vacuous-pass demonstrations, all on `/tmp/claude-0/w29/tree`:**

```
D1  rm research/literature/news-match-queue.json ; python3 scripts/news_match.py --check
    news_match --check: no queue committed yet — nothing to validate
    rc=0

D2  (ledger "rows" set to [])       ; python3 scripts/citation_debt.py --check
    citation debt: 0 record(s), 0 destination(s)
       every declared destination is decided and every discharge verified
    rc=0

D3  rm research/manuscripts/emc-systems-map.json ; python3 scripts/trigger_scan.py --check
    trigger_scan --check: registry not found at …/emc-systems-map.json — skipping cross-check
    rc=0

D5b (registry restored, "triggers" set to []) ; python3 scripts/trigger_scan.py --check
    trigger_scan --check: 0 ERROR across 0 trigger(s); 27 registry revival_trigger field(s) seen
    rc=0

D6  (committed drift block replaced by render(*measure()) with .git absent — the UNKNOWN block)
    python3 research/manuscripts/aso_deposit_drift.py --check
    rc=0     [committed block reads: "⚠ The drift cannot be measured here … UNKNOWN, which is not the same as zero"]

D4b rm research/modalities/atr-hrd-sarcoma-series.json ; python3 research/modalities/atr_hrd_sarcoma_series.py --check
    IDENTITY UNBOUND — ART-ATR-HRD-SERIES does not hold GSE299349
        B/artifact: missing file: research/modalities/atr-hrd-sarcoma-series.json
    artifact written from the cache
    rc=1
    $ sha256sum research/modalities/atr-hrd-sarcoma-series.json
    d469cb27c8e5d2c3aba94de8486ddbebff49497f2b392adc665c3ac690ae102c   ← the file --check re-created
```

**RUN — proxy characterisation:** verbatim outputs in R3.

**PROPOSED (NOT RUN):** the row-3 (`submission_citations.py`) vacuous path was derived from source only — I did not construct a manuscript with zero annotated superscripts, and I did not delete `origin/literature-cache` to demonstrate the ungated metadata half. Both are executable on a scratch copy; neither was executed.

## Limitations

- **Row 3's vacuous path is source-derived, not demonstrated.** Four of the five are demonstrated with real exit codes; that one is not, and the count "5 of 18" therefore rests on 4 measurements plus 1 code reading.
- **The scratch copy has no `.git`.** Free disk fell to 1.5 GB, so I did not copy the 365 MB object store. Rows 9, 10 and 13 read git state, so their scratch behaviour is the *degraded-provenance* behaviour, not the normal one; I compensated by running 9 and 10 read-only in the live tree.
- **"Vacuous" here means an exit-0 that asserts nothing beyond a parse.** It is not a claim that any of the five artifacts is currently empty, absent or wrong — all 18 rows are green at the live HEAD with real data behind them. It is a claim about what the gate would *fail to notice*.
- **I did not measure whether any vacuous path is reachable in practice** — e.g. how a queue file would come to be absent on a real branch. Reachability-in-practice is UNKNOWN, not zero.
- I did not run `scripts/preflight.sh`, so I make no claim about the gate as a whole, only about these 18 invocations.
- Row 13's write was demonstrated on a scratch copy with the artifact deliberately deleted. I did not delete anything in the live tree.
- No repair is proposed, authored, applied or tested; no guard was weakened or reordered. No clinical claim; there is no wet lab.

## Stop condition

**Set at the outset:** return as soon as (a) all 18 `--check` bodies are read in source and classified on the five axes, (b) the vacuous-pass count is stated with per-row source evidence, (c) at least two are demonstrated with real exit codes, and (d) the network question is answered with an actual proxy observation.

**MET.** (a) 18/18 read and tabled; (b) 5 of 18, each with the quoted line that makes it vacuous; (c) **four** demonstrated (D1, D2, D3+D5b, D6), plus D4b demonstrating a tree write during `--check`; (d) answered — 0 of 18 `--check` paths issue HTTP, the one git-fetch path is not taken here, and the two denied hosts (`eutils.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`, both CONNECT 403) are unreachable from any `--check` path.

## Tool-call and wall-clock count actually used

**26 tool calls**, **~6 minutes wall clock** (`date -u` 03:14:07Z → 03:19:54Z). Well inside the ~40/~40 target.

## Next concrete action

**Measure whether each of the five vacuous paths is reachable from a plausible commit, and give the gate a per-row "what did this row actually examine?" count.** Concretely: for rows 16, 17 and 18 the fix-shaped question is whether the denominator each already prints (`0 ERROR across N trigger(s)`, `N record(s), M destination(s)`, `N queued item(s)`) can be compared against a committed floor — the pattern `single_slot_identity.py` already implements for its registry and is the only working precedent in the 18. That successor is read-only, needs no write authority, and reuses `/tmp/claude-0/w29/tree` unchanged. It should go to whoever owns the gate, not to a fresh read-only lane, because unlike this unit it ends in a change.
