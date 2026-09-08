<!-- collected 2026-09-08T03:38:26Z by campaign coordinator; agent id acdc9f337c6e4fdb3; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-acdc9f337c6e4fdb3.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W16g**, LANE 16 fifth refill — closing the eight-module regeneration-identity residual W16f left open.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am powered by Opus 5, exact model ID `claude-opus-5`. I did not observe the served model and do not assert it as fact. No environment variable in this container names a served model.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:30:55 UTC 2026` | `Tue Sep  8 03:35:14 UTC 2026` |
| `git rev-parse HEAD` | `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1` | `1c9d827870599576c0c027a9134363d59456fd04` |
| `git status --porcelain` | **empty** | **empty** |

**The tree moved under me** (`215ed8e7` → `1c9d8278`; the coordinator is committing campaign reports). **My `tar --exclude=./.git` snapshot was taken at `215ed8e7`, and every measurement below is against `215ed8e7` and only that**, except two runs explicitly marked as executed read-only in the live checkout (`expression_validation_readiness --check`, and the `git`-backed regeneration of `surface_address_sensitivity`, which resolved `HEAD` to `215ed8e7` at run time — see §4).

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at end (identical set at start; long proxy/truststore lines truncated to 90 columns by `cut`, none contains a model identity):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 -Djavax.net.ss
NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.ant
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

## Stop condition (stated up front)

Return the moment all four hold: (1) each of W16f's eight unmeasured modules has, from source, a stated identity-test procedure; (2) every one of the eight that is testable offline without network has been tested and reported IDENTICAL / DIFFERS-with-fields / UNMEASURED-with-a-specific-reason, with a real exit code; (3) W16f's cluster size is either a measured number or has a precisely named residual unknown; (4) W16f's "no GSE24369 series matrix exists in the tree" correction is independently verified.

**All four hold. Stop condition MET.**

---

## Question

**Which of the eight panel-consumer modules whose regeneration identity W16f could not measure are actually testable in this environment, what do they say when tested, and does that turn "at least six and unbounded above" into a bounded number?**

Open because W16f measured 13 of 21 panel consumers and explicitly labelled eight unmeasured — one killed by its own 120 s timeout, two argv-gated, five with no module-level `OUT` — and stated the cluster is therefore unbounded above.

---

## Prior-work check

Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W16f-gse24369-drift-diagnosis.md`. `reports/W16d-unpinned-pooled-figures.md` and `reports/W16e-regeneration-identity-check.md` were located and sized (389 and 322 lines) but not read line-by-line; W16f's report reproduces and corrects W16e's findings and is the residual I was dispatched against. **This is a limitation, stated as one, not a claim of full coverage.**

Commands actually run:

```
git ls-files | grep -i "GSE24369"
find . -name "*GSE24369*" -not -path "./.git/*"
find . -name "*series_matrix*" -not -path "./.git/*"
grep -rn "GSE24369" --include=*.py .
grep -l "emc-expression-panels.json" research/modalities/*.py
git rev-list --count HEAD ; git log --format='%h %p' | tail -2
git cat-file -t 8c1f292536b7d725186491b42c19c87c0b6c855c
```

**Not replaying W16f.** I did not re-run the three original identities, the 22-module sweep, the provenance-stamp scan or the panel-value reads; I take those as W16f measured them and go only to the eight it named unmeasured. **I did not touch, argue or resolve the `bishop2019` per-pool clause** — it plays no part in anything below. **I did not decide which side of the drift is stale**; that remains the data owner's call, exactly as W16f left it. `CLOSED-WORK.md` records `GSE24369`-family data as heavily retained; I read no new source and add no new data.

---

## Method / inputs

Read-only on the Git tree. Executed on a `tar --exclude=./.git` scratch copy at `/tmp/claude-0/w16g/tree/` taken at HEAD `215ed8e7`; **that directory was deleted before returning** (`rm -rf /tmp/claude-0/w16g`; `ls` → `No such file or directory`; free space `20G → 21G`). Nothing under `/home/user/Rare-cancers` was created, edited or deleted; `git status --porcelain` was empty at start and end; no git write operation was run; `scripts/preflight.sh` was not run.

**Environment:** system `python3` = **3.11.15**, stdlib only. All runs with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPYCACHEPREFIX=/tmp/claude-0/w16g/pyc`.

**No network.** No GEO series matrix and no external input was fetched. One module (`emc_surface_normal_window`) is a pure network client; see §3 for why I did not run it and what I established instead.

Method per module: read the module's `main`/argparse from source; establish whether its `--check` path **provably** returns before any `open(..., "w")`; where a `--check` exists and is provably non-writing, run it and quote the real exit code; where no `--check` exists or `--check` does not actually compare against the committed artifact, regenerate into the scratch copy and diff every JSON leaf against the committed artifact copied aside beforehand (recursive leaf walk, absent leaves included).

---

## Result

### 1 · Independent verification of W16f's premise correction · PRIMARY

**Verified. There is no GSE24369 series matrix in this tree, and no series matrix of any kind.**

```
$ git ls-files | grep -i "GSE24369"
research/autonomy/opus-capacity-campaign-20260908/reports/W16f-gse24369-drift-diagnosis.md
$ find . -name "*GSE24369*" -not -path "./.git/*"     → (no output)
$ find . -name "*series_matrix*" -not -path "./.git/*" → (no output)
```

The single `git ls-files` hit is **W16f's own report**, committed after W16f ran. Every `GSE24369_series_matrix.txt.gz` occurrence in Python is a bare string literal used as a **dictionary key** into committed JSON (e.g. `emc_prmt5_route_controls.py:52`, `emc_prmt5_effect_sizes.py:62`, `emc_mtap_prmt5_figures.py:54`, `nr4a3_fusion_targets.py:95`). **The string is never opened.** W16f's correction stands, verified independently at a different commit before I relied on it.

I also independently confirm the pass-through shape by a structural test W16f did not run (§2): membership in the drift cluster requires a **code-path** read of `emc-expression-panels.json`, and three of W16f's eight "consumers" do not have one.

### 2 · Code-path consumers vs. grep-level mentions — a correction to the candidate set · PRIMARY

22 files under `research/modalities/` contain the string `emc-expression-panels.json`; one is the producer (`emc_expression_panels.py:69`), so **21 consumers**, which reconciles W16f's 13 measured + 8 unmeasured. But an AST pass (string constants excluding module/function/class docstrings) shows three of the eight reference the panel **only in prose**:

| Module | code-path string refs | Verdict |
|---|---|---|
| `atr_hrd_sarcoma_series` | **0** (line 61 is a `#:` comment) | **not a panel consumer** |
| `single_slot_identity` | **0** (line 58 is a docstring) | **not a panel consumer** |
| `emc_surface_normal_window` | 1, line 269 — inside a `_pairs_with` **provenance prose string** in the output dict; the module's only `open()` calls are `OUT` (line 153, its own prior artifact) and `urllib.request.urlopen` (line 91) | **not a panel consumer** |

**Structural consequence: those three cannot be members of the panel-drift cluster regardless of whether their identity is measurable.** This tightens the bound in §4 far more than any single test did.

### 3 · The eight residuals, each resolved · PRIMARY

| # | Module | What identity testing requires (from source) | Verdict | Exit |
|---|---|---|---|---|
| 1 | `aso_delivery_antigen` | `main(argv)`; `--check` at line 833 compares **only** `per_antigen` and `headline` and `return`s at 843, **before** the `open(OUT,"w")` at 845 — provably non-writing. But that is a *partial* identity, so I also regenerated and diffed the whole artifact. | **IDENTICAL** — `--check` "per_antigen and headline reproduce exactly"; full-artifact leaf diff **0 differing leaves of 845** | 0 |
| 2 | `emc_tissue_read_statistics` | `main(argv)`; `--check` at 425 prints a count and `return 0` before the `open(OUT,"w")` at 429 — provably non-writing, **but it never reads the committed artifact at all: it is not an identity check.** So the only valid test is regenerate-and-diff. | **IDENTICAL** — full-artifact leaf diff **0 differing leaves of 3847** | 0 (regen), 0 (`--check`) |
| 3 | `emc_mtap_prmt5_figures` | `--check` (argparse, line 445) compares content hashes of its four source artifacts against `research/manuscripts/figures/mtap-prmt5-figure-provenance.json`; the only write (line 415) is in the draw path. Non-writing. | **DIFFERS** — `DRIFT emc-expression-panels.json: stamped 38233b8ebf557d48, now 123bd05a9f9f5d08`; also `DRIFT census-route-expression-grading.json: stamped a21cdbebdda19710, now 5bc3c80c034dde77` | **1** |
| 4 | `surface_address_sensitivity` | No `--check`; `main()` writes `OUTPUT` and `NOTE` unconditionally; needs `git rev-parse HEAD` and `git show REV:path` (line 214/219). Test = regenerate in scratch with `GIT_DIR` pointed at the live object store (read-only git), then diff. | **DIFFERS in exactly one leaf, and it is run-context, not content:** `.provenance.base_revision: '7aa73894…' -> '215ed8e7…'` (= `git rev-parse HEAD` at run time). All **8884** other leaves identical, including the parent panel SHA256. The `.md` differs on the same one substring. | 0 |
| 5 | `atr_hrd_sarcoma_series` | argparse `--check`; the `open(art_path,"w")` at 1453 is guarded by `if not os.path.exists(art_path)`, and the artifact exists, so no write. Not a panel consumer (§2). | **IDENTICAL** — "OK — the slot is bound to GSE299349"; "OK — the artifact re-derives byte-identically from the committed inputs cache" | 0 |
| 6 | `single_slot_identity` | argparse `--check`; a registry guard, no write. Not a panel consumer (§2). | **IDENTICAL / PASS** — "OK ART-ATR-HRD-SERIES bound to GSE299349 (artifact, 2 caches, systems map, 1 declaring document(s))" | 0 |
| 7 | `expression_validation_readiness` | argparse, mutually exclusive `--write`/`--check`; `--check` writes nothing (`path.write_bytes` only under `args.write`). But it reconstructs its inputs with `git show {BASE}:{path}` where `BASE` is **hard-pinned to `8c1f292536b7d725186491b42c19c87c0b6c855c`**. | **UNMEASURED — specific reason: that base revision does not exist in this repository's object database.** `git cat-file -t 8c1f2925…` → `fatal: git cat-file: could not get object info`. The run dies in `Audit.__init__` at line 57: `fatal: path 'research/modalities/emc-expression-panels.json' exists on disk, but not in '8c1f2925…'`. **Not failing, not passing.** | **1** (crash, `CalledProcessError`) |
| 8 | `emc_surface_normal_window` | No `--check`; `main()` writes `OUT` unconditionally (line 279). Its inputs are **46 live HTTP queries to `proteinatlas.org/api/search_download.php`** (18 `GENES` + 28 `GENES_BY_SYMBOL`), each with 4 retries and 1+2+4 s backoff plus a 0.3 s pace — **a lower bound of ~336 s of pure sleep with the network down**, which is why W16f's 120 s timeout killed it. | **UNMEASURED — and, unlike W16f's timeout, this is now a proved structural reason rather than an unfinished run.** See below. | not run |

**On #8, why a generous timeout is the wrong instrument.** I was dispatched to give it more time. Reading the source changed the answer, and I report the change rather than the instruction. `_get_json` returns `None` on exhausted retries, and `main()` then writes `{"_status": "no HPA record"}` for that gene. The committed `emc-surface-normal-window.json` holds **46 antigens, 45 with populated live HPA fields and 1 recorded `symbol mismatch — record DISCARDED`** — i.e. it was built online. **So an offline run of any duration produces an artifact that differs from the committed one at essentially every leaf, by construction, and that "DIFFERS" would measure the absence of network, not drift.** Running it would also be a fetch of an external input, which my dispatch prohibits. **PROPOSED (NOT RUN):** re-run `emc_surface_normal_window.py` in an environment with HPA reachable and diff against the committed artifact. Verdict here: **UNMEASURED — no offline reproduction path exists; not testable in this environment at any timeout.** Its cluster membership is nonetheless **settled negatively** on structural grounds (§2): it never opens the panel.

### 4 · The cluster size, now bounded · PRIMARY

Full accounting of all **21** consumers of `emc-expression-panels.json`:

| Class | n | Modules |
|---|---|---|
| **Drift-cluster members (DIFFERS, panel-driven)** | **7** | `emc_proteostasis_read`, `emc_prmt5_route_controls`, `emc_mtap_locus_persample`, `emc_hypoxia_confounds`, `emc_prmt5_effect_sizes`, `emc_prmt5_multiplicity` (all six W16f) **+ `emc_mtap_prmt5_figures` — new this run** |
| Measured clean (IDENTICAL / reproduces) | 8 | W16f's 5 (`nr4a3_fusion_targets`, `census_route_expression_grading`, `emc_dkk1_lineage_controls`, `emc_fourth_cohort_route_readout`, `ndrg1_panel_attribution`) **+ `aso_delivery_antigen`, `emc_tissue_read_statistics`, `surface_address_sensitivity` — new this run** |
| DIFFERS for a **different**, non-panel cause | 2 | `alcam_precedent`, `cd248_precedent` (`origin/literature-cache` unreachable → `_status: READ → UNREAD`) |
| Prose-only mention, **structurally excluded** from the cluster | 3 | `atr_hrd_sarcoma_series`, `single_slot_identity` (both also green on their own `--check`), `emc_surface_normal_window` (identity unmeasurable, membership excluded) |
| **Membership genuinely UNKNOWN** | **1** | **`expression_validation_readiness`** — a real code-path consumer (`FILES["panels"]`, line 20) whose `--check` cannot run here because its pinned `BASE` revision is absent from the object DB |

⭐ **The measured answer: the cluster is SEVEN committed artifacts — six JSON data artifacts plus one figure-provenance stamp — and it is bounded above by EIGHT.** W16f's "unbounded above" is replaced by exactly one named residual: **`expression_validation_readiness` is the only module in this repository whose panel-drift membership is unknown**, and it is unknown for one specific, stateable reason (a dangling pinned base revision), not for a timeout, an argv, or a missing `OUT`.

The 7th member's evidence is worth stating plainly for the owner: `emc_mtap_prmt5_figures`' provenance stamp records the panel at `38233b8e…`, while the committed panel now hashes `123bd05a…` — and `123bd05a…` is exactly the hash `surface_address_sensitivity`'s committed artifact already records as its parent. **So two committed artifacts disagree about which panel is current, and they disagree in the direction W16f's stamp-gap evidence predicted: the figure stamp is on the old side, `surface-address-sensitivity.json` is on the new side.** That is decision evidence for the owner. **I am not deciding it.**

**No clinical claim of any kind.** Every number above is an internal file-consistency measurement over committed artifacts. A transcriptomic percentile is an **ASSOCIATION**, never a mechanism; nothing here bears on efficacy, safety, selectivity, therapeutic window, prognosis or clinical readiness, and there is no wet lab.

---

## Validation evidence

**RUN.** All under `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w16g/pyc`, `python3` 3.11.15. Scratch tree `/tmp/claude-0/w16g/tree` from HEAD `215ed8e7` unless a row says "live repo".

| # | Command | Exit | Key output |
|---|---|---|---|
| 1 | live repo: `date -u; git rev-parse HEAD; git status --porcelain` (start) | 0 | `03:30:55Z`; `215ed8e7…`; status **empty** |
| 2 | `tar --exclude=./.git -cf - . \| (cd …/tree && tar -xf -)` | 0 | `COPY_OK`, 613M |
| 3 | live repo: `git ls-files \| grep -i GSE24369`; `find . -name "*GSE24369*"`; `find . -name "*series_matrix*"` | 0/0/0 | only W16f's own report; **no matrix file of any kind** |
| 4 | `python3 <m>.py --check` for `aso_delivery_antigen`, `emc_tissue_read_statistics`, `single_slot_identity`, `emc_mtap_prmt5_figures`, `atr_hrd_sarcoma_series` (each `timeout 600`) | **0, 0, 0, 1, 0** | verbatim in §3; `emc_mtap_prmt5_figures` → `DRIFT emc-expression-panels.json: stamped 38233b8ebf557d48, now 123bd05a9f9f5d08` |
| 5 | `find …/tree/research/modalities -newermt '-10 minutes' -name '*.json'` after those five | 0 | **no output** — the five `--check` runs wrote nothing, as read from source |
| 6 | `cp` four committed artifacts to `/tmp/claude-0/w16g/orig/` (live repo, read-only source) | 0 | 4 files, 53488 / 90201 / 467337 / 9105 bytes |
| 7 | `timeout 600 python3 aso_delivery_antigen.py` (scratch, full regen) | **0** | — |
| 8 | `timeout 600 python3 emc_tissue_read_statistics.py` (scratch, full regen) | **0** | `wrote research/modalities/emc-tissue-read-statistics.json` |
| 9 | `python3 diff.py orig/… tree/…` (recursive leaf walk) ×2 | 0 | `aso-delivery-antigen: IDENTICAL n_differing_leaves=0 n_leaves_committed=845`; `emc-tissue-read-statistics: IDENTICAL n_differing_leaves=0 n_leaves_committed=3847` |
| 10 | `GIT_DIR=/home/user/Rare-cancers/.git timeout 600 python3 surface_address_sensitivity.py` (scratch) | **0** | `{"outputs": [...], "states": {"stable_negative":5,"stable_positive":7,"unreadable":3,"unstable":7}}` |
| 11 | `python3 diff.py` + `diff` on the `.md` | 0 / **1** | `DIFFERS n_differing_leaves=1 n_leaves_committed=8885`; `.provenance.base_revision: '7aa73894f4717705276b9cfa02d05d3799be98cf' -> '215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1'` — the sole leaf |
| 12 | live repo: `timeout 600 python3 research/modalities/expression_validation_readiness.py --check` | **1** | `fatal: path 'research/modalities/emc-expression-panels.json' exists on disk, but not in '8c1f2925…'` + `CalledProcessError` traceback at line 57 |
| 13 | live repo: `git cat-file -t 8c1f2925…`; `git rev-list --count HEAD`; `git log --format='%h %p' \| tail -2` | 128/0/0 | `could not get object info`; **346**; `14a3f172` has empty parents (root) |
| 14 | AST pass over the 22 panel-mentioning files (docstring-excluding constant scan) | 0 | `atr_hrd_sarcoma_series=0`, `single_slot_identity=0`, `emc_surface_normal_window=1` (line 269, prose) |
| 15 | `grep -n "open(\|json.load" emc_surface_normal_window.py`; AST gene count | 0 | opens only `OUT` and `urlopen`; **46 queries**, ≥336 s sleep floor offline |
| 16 | live repo: committed `emc-surface-normal-window.json` composition | 0 | `antigens: 46`; `Counter({'<has HPA fields>': 45, 'symbol mismatch — record DISCARDED': 1})` |
| 17 | live repo: `date -u; git rev-parse HEAD; git status --porcelain` (end) | 0 | `03:35:14Z`; `1c9d8278…`; status **empty** |
| 18 | `rm -rf /tmp/claude-0/w16g`; `ls -d`; `df -h /` | — | `No such file or directory`; free `20G → 21G` |

One tool call was **denied by the auto-mode classifier** (a compound `set -x` + `cp` + `GIT_DIR=… python3` line). I did not work around the intent: I split it into the separate, individually-approved calls #6, #7, #8, #10 above. No guard was weakened, no acceptance criterion authored or relaxed, no repair written.

**PROPOSED (NOT RUN):** (a) `emc_surface_normal_window.py` with HPA reachable, then diff — the only way its identity can be measured, and out of scope under my no-network instruction; (b) `expression_validation_readiness.py --check` in a checkout whose object DB contains `8c1f2925…`. Both **UNKNOWN** here.

---

## Limitations

- **The tree moved under me** (`215ed8e7` → `1c9d8278`). All scratch measurements are pinned to `215ed8e7`.
- **`surface_address_sensitivity` was regenerated against the live object store** via `GIT_DIR`, so its one differing leaf is `HEAD` at run time. Had a coordinator commit landed mid-run, that leaf would name a different commit; the finding — *exactly one leaf differs and it is `base_revision`* — is unaffected.
- **`emc_surface_normal_window`'s identity remains genuinely unmeasured.** I proved it is unmeasurable offline; I did not measure it. Its *cluster membership* is settled (negative, structurally), its *identity* is not.
- **`expression_validation_readiness` is the one open residual.** Its `--check` might also fail for further reasons past line 57 that I never reached.
- **I did not read W16d or W16e in full**, only W16f. Anything W16d/W16e established that W16f did not carry forward is outside my coverage.
- **`emc_mtap_prmt5_figures`' `--check` is a source-hash staleness check, not a figure re-derivation.** It proves the drawn figures were made from a different panel than the one committed; it does not prove any drawn value changed. Redrawing would need `matplotlib` and was not attempted.
- **`aso_delivery_antigen`'s and `emc_tissue_read_statistics`'s IDENTICAL verdicts are whole-artifact leaf equality**, which is stronger than their own `--check` — but a reordered list would register as many differing leaves, so leaf counts are leaf counts, not independent quantities.
- **No clinical, efficacy, safety, selectivity or prognosis claim** is made or implied. Nothing here resolves, argues or touches the `bishop2019` per-pool clause. **I did not decide which side of the drift is stale.**

---

## Stop condition

Stated up front; **MET**. All eight residuals have a source-derived test procedure; six of the eight were tested with real exit codes (four IDENTICAL, one DIFFERS with its differing hashes, one DIFFERS in a single run-context leaf); two are UNMEASURED with specific, non-timeout reasons. The cluster is a measured **7**, bounded above by **8**, with exactly one named unknown. W16f's no-series-matrix correction verified independently. Returning now.

---

## Tool-call and wall-clock count actually used

**22 tool calls** (all Bash; one denied by the classifier and re-run split). **Wall clock 03:30:55Z → 03:35:14Z = 4 min 19 s** of measurement, plus report drafting. Well inside the ~40/~40 target.

---

## Next concrete action

**One finite task, and it is a diagnosis, not a repair:** determine whether `expression_validation_readiness.py`'s pinned `BASE = "8c1f292536b7d725186491b42c19c87c0b6c855c"` names a commit that ever existed in this repository — `git rev-list --count HEAD` is 346 with root `14a3f172`, and the object is absent — and if it does not, report to the owner of `research/modalities/expression_validation_readiness.py` that the module's `--check` has been **inert since that revision went missing**, exiting 1 on a `git` failure rather than on an artifact comparison. That single determination closes the last unknown in the cluster accounting: with `--check` runnable, the number becomes exactly 7 or exactly 8. **Explicitly not the next action:** repointing `BASE`, or adding any identity guard to the seven drifting artifacts — seven are red today, and W16f is right that a guard which is red at commit time is a broken gate. The `BASE` question is the owner's to answer, and the identity guards go in after the which-side-is-stale decision, not before.
