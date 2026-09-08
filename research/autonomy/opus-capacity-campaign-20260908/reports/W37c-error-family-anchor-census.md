<!-- collected 2026-09-08T04:45:25Z by campaign coordinator; agent id aa4d85386ed09c2af; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aa4d85386ed09c2af.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted, live tree untouched. Report follows.

---

## Worker

**W37c** — successor to W37b, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: the anchor-class census of `systems/systems_check.py`'s error families.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am Claude Opus 5, exact model ID `claude-opus-5`. Nothing in my environment independently confirms a served model — `env` carries no model variable. The coordinator must extract the actual per-child runtime model from the transcript.

- `date -u` start `Tue Sep  8 04:38:48 UTC 2026` · end `Tue Sep  8 04:41:35 UTC 2026`.
- `git rev-parse HEAD` start **`408b676aec3625a36917755662516232a27a1278`** · end **`7a1002679e0830fb19bed48660772cdcc91c495d`**. HEAD moved under me (coordinator collection). **Verified rather than assumed:** `git diff --name-only 408b676a 7a100267 | grep -v opus-capacity-campaign-20260908` → **0 files**. Nothing I read changed.
- `git status --porcelain` start **0 lines** · end **0 lines**.
- **Write isolation honoured.** No file created, edited, moved or deleted under `/home/user/Rare-cancers`; only read-only git commands (`rev-parse`, `status`, `diff --name-only`); `scripts/preflight.sh` not run; `systems_check.py` never invoked (this was a pure source reading — I ran no `--check` and no `--write-views`); `atr_hrd_sarcoma_series.py` never invoked; no patch, gate, test or repair authored or proposed; no guard weakened, narrowed or reordered. All execution under `/tmp/claude-0/w37c/`, now **deleted** (`ls` → "No such file or directory"; `/` at 17 G free, 55%). No network.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; the four long proxy-list variables `GLOBAL_AGENT_NO_PROXY`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` are shown elided where they repeat the `no_proxy` value verbatim):

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

Env output at end was identical (same process, no variable set or unset by me).

## Question

W37b measured by execution that `systems/systems_check.py --check` does **not** have the regenerate-then-check escape: emptying all 15 `COLLECTIONS` and running the module's own remedy `--write-views` leaves **123 ERROR, exit 1**, in three families — `[L2]` 89, `[W1]` 18, `[M2]` 16 — because their assertions have a second home the regenerator does not own. W37b read the error *text*, not the raise sites, and settled only those three.

**My bounded question:** enumerate **every** error family `systems_check.py` emits, and for each determine **by source reading** whether its assertion is anchored (i) only to generated views, (ii) only to graph JSON, or (iii) to a cross-source pair. Then state precisely which families would become escapable if the regenerator's ownership widened, and name the specific ownership change that would do it.

Open because W37b's own Limitations section says the mechanism was "read off the verbatim error text and the histogram, not off the raise sites, which I did not open," and because a three-family answer cannot say what the *rest* of the gate's protection rests on.

## Prior-work check

- Read in full, as instructed: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W37b-systems-check-regenerate-identity.md`, and the head + section index of `reports/W37-zero-test-coverage-beyond-18-rows.md` (all under `research/autonomy/opus-capacity-campaign-20260908/`).
- Honoured the brief's "Known, measured, and NOT worth rediscovering": I did **not** re-measure the `--check` error baseline (100% this campaign's own directory, ~87% `[D4]`), did **not** re-verify the 0-of-89 resolution rate, did **not** re-run W37b's emptying experiment, and did **not** run `python3 -m pytest`.
- `grep -rn "extractor" --include=*.py systems/ research/ scripts/`, `grep -rln "emc-systems-map" --exclude-dir=.git --exclude-dir=opus-capacity-campaign-20260908 .`, `grep -rn "emc-systems-map" --include=*.py --include=*.mjs --include=*.sh . | grep -iE 'open\(|"w"|write|dump'` — used to establish which of the cross-source anchors already has a generator. These found real repository files (`systems/extract_requirement_register.py`, `systems/extract_plan.py`), not sibling reports.
- **W25 not read, not referenced.**
- Per W35: campaign reports are not repository evidence. My only claim of novelty is the raise-site anchor census, which exists nowhere in the tracked corpus.
- **Per W38b: `systems/systems_check.py` is one of the two line-shifted files.** Every `:NN` citation below was resolved in the **live checkout** at `408b676a`, not in the frozen corpus.

## Method and inputs

| Input | Value |
|---|---|
| File under census | `/home/user/Rare-cancers/systems/systems_check.py`, **4591 lines**, at HEAD `408b676a` (byte-identical at `7a100267`) |
| Method | Static source reading only. Three throwaway `python3` scripts in `/tmp/claude-0/w37c/` parsed the file with `ast` and `re` to map every `[Xn]` literal to its **enclosing top-level `def`**, and to record which source roots each check function touches (`g[...]`, `VIEWS`, `GRAPH`, `SCHEMA`, `REPO`, `LEGACY`, `MAP_DOC`, `SCAN_TRIGGERS`, `PINNED`, `RELATIONS`, `LINK_BASELINE`, `INSTRUCTION_SKILLS`, and the repo-reading helpers). Every classification was then confirmed by reading the raise site and its surrounding block. |
| Regenerator definition | `write_views()` `:4524-4532` writes `all_views(g)` `:4502-4522` into `VIEWS = systems/views` (`:36`) and **nothing else**. It is the only write path in the module. |
| Emptying attack | as W37b ran it: the 15 `COLLECTIONS` (`:38-63`) set to `[]`. `plan.json`, `integrity.json`, `relations.json`, `artifact-refs.json`, `link-baseline.json` live under `systems/graph/` but are **not** `COLLECTIONS` and are not emptied. |

**Anchor classes.** The dispatch's trichotomy needed a fourth cell, because a large share of families consult the graph not at all:

- **(i) VIEW** — compares `systems/views/**` against an in-memory render of the graph.
- **(ii) GRAPH** — anchored wholly inside the 15 `COLLECTIONS` (one collection, or two collections cross-referenced). Vacuous when the graph is empty: zero rows, zero iterations.
- **(iii) CROSS** — a pair, one side a `COLLECTIONS` file and one side something else.
- **(iv) NON-GRAPH** — anchored wholly outside both the graph and the views. Neither emptying the graph nor regenerating views can touch these. **This class is not in the dispatch's trichotomy and it is the largest one.**

## Result

### R1 — The full family census (`PRIMARY`, by source reading)

**72 distinct code literals appear in the file; 68 are actually raised.** Codes are **reused across different check functions** (`[B1]`–`[B5]`, `[P1]`, `[K1]`, `[K2]`, `[X1]`, `[X2]`, `[X4]` each raise from two different checks against different anchors), so the honest unit of a "family" is the **(code, check function)** pair. All line numbers are `systems/systems_check.py:NN` in the live checkout.

| Check id | Emitting file:line | Check function | Sev | Anchor class | Other home (non-graph side) |
|---|---|---|---|---|---|
| `[G1]` | `:4540` | `check_views` | ERR | **(i) VIEW** | — |
| `[G2]` | `:4544` | `check_views` | ERR | **(i) VIEW** | — |
| `[S0]` | `:196` | `SchemaSet.check_schemas_are_themselves_valid` | ERR | **(iv) NON-GRAPH** | `systems/schema/*.json` vs metaschema |
| `[S1]` | `:503` | `check_schemas` | ERR | **(iii) CROSS** | `systems/schema/*.schema.json` |
| `[S2]` | `:518` | `check_schemas` | ERR | **(iii) CROSS** | `systems/schema/technology.schema.json` |
| `[S3]` | `:513`, `:523` | `check_schemas` | ERR | **(iii) CROSS** | `systems/schema/*.schema.json` |
| `[L1]` | `:1074` | `check_legacy_agreement` | ERR | **(iv) NON-GRAPH** | `research/manuscripts/emc-systems-map.json` (existence) |
| `[L2]` | `:1093` | `check_legacy_agreement` | ERR | **(iii) CROSS ⭐** | legacy registry — **survives emptying (89)** |
| `[L3]` | `:1097` | `check_legacy_agreement` | ERR | **(iii) CROSS** | legacy registry (field disagreement) |
| `[L4]` | `:1100` | `check_legacy_agreement` | WARN | **(iii) CROSS** | legacy registry (graph-side direction) |
| `[I1]` | `:532` | `check_ids_unique` | ERR | **(ii) GRAPH** | — |
| `[H1]` | `:543`, `:545` | `check_hierarchy` | ERR | **(ii) GRAPH** | — |
| `[H2]` | `:551` | `check_hierarchy` | ERR | **(ii) GRAPH** | — |
| `[H3]` | `:554` | `check_hierarchy` | ERR | **(ii) GRAPH** | — |
| `[B1]` | `:578` | `check_publications` | ERR | **(ii) GRAPH** | — |
| `[B2]` | `:584` | `check_publications` | ERR | **(ii) GRAPH** | — |
| `[B3]` | `:588` | `check_publications` | ERR | **(ii) GRAPH** | — |
| `[B4]` | `:602` | `check_publications` | ERR | **(iii) CROSS** | the publication's `document.file` frontmatter |
| `[B5]` | `:614` | `check_publications` | WARN | **(ii) GRAPH** | — |
| `[B6]` | `:618` | `check_publications` | INFO | **(ii) GRAPH** | — |
| `[B7]` | `:626` | `check_publications` | INFO | **(iii) CROSS** | `_walk_md(DOC_SKIP)` L3-declaring documents |
| `[B1]` | `:636` | `check_blockers` | ERR | **(ii) GRAPH** | — |
| `[B2]` | `:639` | `check_blockers` | ERR | **(ii) GRAPH** | — |
| `[B3]` | `:642` | `check_blockers` | WARN | **(ii) GRAPH** | — |
| `[B4]` | `:648` | `check_blockers` | ERR | **(ii) GRAPH** | — |
| `[B5]` | `:652` | `check_blockers` | ERR | **(ii) GRAPH** | — |
| `[T1]` | `:660`, `:662` | `check_technologies` | ERR | **(ii) GRAPH** | — |
| `[T2]` | `:664` | `check_technologies` | ERR | **(ii) GRAPH** | — |
| `[T3]` | `:672` | `check_technologies` | WARN | **(ii) GRAPH** | — |
| `[T4]` | `:677` | `check_technologies` | WARN | **(ii) GRAPH** | — |
| `[T5]` | `:681` | `check_technologies` | ERR | **(ii) GRAPH** | — |
| `[T6]` | `:685` | `check_technologies` | WARN | **(ii) GRAPH** | — |
| `[P1]` | `:717` | `check_pointers` | ERR | **(iii) CROSS** | the owner file named by the row, on disk |
| `[P2]` | `:721` | `check_pointers` | ERR | **(iii) CROSS** | that file's heading anchors (`anchor_resolves` `:759`) |
| `[V1]` | `:786` | `check_instrument_support` | ERR | **(ii) GRAPH** | — |
| `[V2]` | `:790` | `check_instrument_support` | ERR | **(ii) GRAPH** | — |
| `[V3]` | `:799` | `check_instrument_support` | ERR | **(ii) GRAPH** | — |
| `[V4]` | `:847` | `check_supporting_evidence_refs` | ERR | **(ii) GRAPH** | — |
| `[B8]` | `:887` (WARN), `:899` (ERR) | `check_trigger_blocker_agreement` | both | **(iii) CROSS** | `research/method-watch-triggers.json` |
| `[B9]` | `:908`, `:913`, `:916` | `check_trigger_blocker_agreement` | ERR/INFO/WARN | **(iii) CROSS** | `research/method-watch-triggers.json` |
| `[T7]` | `:952` | `check_revisit_trigger_reachability` | ERR | **(ii) GRAPH** | — |
| `[T8]` | `:991` | `check_closed_carries_no_reopening_trigger` | ERR | **(ii) GRAPH** | — |
| `[Q1]` | `:1009` | `check_requirements` | ERR | **(ii) GRAPH** | — |
| `[Q2]` | `:1011` | `check_requirements` | ERR | **(ii) GRAPH** | — |
| `[Q3]` | `:1020`/`:1024`/`:1029` | `check_requirements` | ERR/WARN/INFO | **(ii) GRAPH** | — |
| `[Q4]` | `:1036` | `check_requirements` | WARN | **(ii) GRAPH** | — |
| `[C1]` | `:1043` | `check_compute_case` | ERR | **(ii) GRAPH** | — |
| `[W1]` | `:1142` | `check_lanes` | ERR | **(iii) CROSS ⭐** | `os.walk(REPO)` `.md/.py/.json/.yml` sweep for `LANE-n` — **survives (18)** |
| `[W2]` | `:1146` | `check_lanes` | WARN | **(iii) CROSS** | same sweep, graph-side direction |
| `[W3]` | `:1172` | `check_lanes` | ERR | **(ii) GRAPH** | — |
| `[W4]` | `:1176` | `check_lanes` | WARN | **(ii) GRAPH** | — |
| `[W5]` | `:1165` | `check_lanes` | WARN | **(ii) GRAPH** | `lanes` × `artifacts` |
| `[M1]` | `:1192` | `check_requirement_source_agreement` | ERR | **(iv) NON-GRAPH** | `research/manuscripts/nr4a3-program-map.md` (existence) |
| `[M2]` | `:1206` | `check_requirement_source_agreement` | ERR | **(iii) CROSS ⭐** | roadmap register — **survives (16)** |
| `[M3]` | `:1208` | `check_requirement_source_agreement` | ERR | **(iii) CROSS** | roadmap register, graph-side direction |
| `[M4]` | `:1213` | `check_requirement_source_agreement` | ERR | **(iii) CROSS** | roadmap claim-ceiling cell |
| `[M5]` | `:1221` | `check_requirement_source_agreement` | ERR | **(iii) CROSS** | roadmap verified-by cell |
| `[X1]` | `:1241` | `check_scan_interop` | ERR | **(iv) NON-GRAPH** | `research/method-watch-triggers.json` (existence) |
| `[X2]` | `:1263` | `check_scan_interop` | ERR | **(iii) CROSS** | `research/method-watch-triggers.json` |
| `[X3]` | `:1275` | `check_scan_interop` | WARN | **(iii) CROSS** | same |
| `[X4]` | `:1281` | `check_scan_interop` | WARN | **(iii) CROSS** | same |
| `[X5]` | `:1271` | `check_scan_interop` | WARN | **(iii) CROSS** | same |
| `[D6]` | `:1356` | `check_doc_ids` | ERR | **(iv) NON-GRAPH** | `_walk_md(ID_SKIP)` frontmatter ids |
| `[D11]` | `:1502`, `:1506`, `:1513` | `check_document_frontmatter` | ERR/ERR/INFO | **(iv) NON-GRAPH** | repo Markdown frontmatter × `document.schema.json` |
| `[P1]` | `:1642`,`:1649`,`:1674`,`:1691`,`:1700`,`:1705` | `check_preflight_gate_list` | ERR | **(iv) NON-GRAPH** | `scripts/preflight.sh` × 4 docs + `.claude/skills/*/SKILL.md` |
| `[P1]` | `:1724`,`:1730`,`:1750`,`:1754` | `check_preflight_gate_ordinal` | ERR/WARN | **(iv) NON-GRAPH** | same pair |
| `[L5]` | `:1775`, `:1781` | `check_evidence_base` | ERR/WARN | **(ii) GRAPH** | — |
| `[D12]` | `:1797`,`:1808`,`:1816`,`:1821` | `check_conventions_template` | ERR | **(iv) NON-GRAPH** | `systems/CONVENTIONS.md` × `document.schema.json` |
| `[D1]` | `:1874` | `check_documents` | ERR | **(iv) NON-GRAPH** | repo Markdown frontmatter |
| `[D2]` | `:1877` | `check_documents` | ERR | **(iv) NON-GRAPH** | same |
| `[D3]` | `:1880` | `check_documents` | ERR | **(iv) NON-GRAPH** | same |
| `[D4]` | `:1913` | `check_documents` | ERR | **(iv) NON-GRAPH** | same — **the ~87% campaign-baseline family** |
| `[D5]` | `:1922` | `check_documents` | WARN | **(iv) NON-GRAPH** | same |
| `[D7]` | `:1898` | `check_documents` | ERR | **(iv) NON-GRAPH** | same |
| `[D8]` | `:1904` | `check_documents` | ERR | **(iv) NON-GRAPH** | + `pinned-figures.json`, `CLAUDE.md`/`AGENTS.md`, `.claude/skills` |
| `[D10]` | `:1893` | `check_documents` | ERR | **(iv) NON-GRAPH** | same |
| `[K2]` | `:2001`,`:2004`,`:2011`,`:2015` | `_artifact_dispositions` | ERR | **(iv) NON-GRAPH** | `systems/graph/artifact-refs.json` (not a `COLLECTIONS` file) |
| `[K2]` | `:2110` | `check_artifacts` | ERR | **(iii) CROSS** | `artifact-refs.json` × `g["lanes"]` |
| `[K1]` | `:2147`,`:2154`,`:2166` | `check_artifacts` | INFO/WARN | **(iii) CROSS** | `_walk_md(DOC_SKIP)` citations × `ARTIFACT_DIRS` × lanes |
| `[K3]` | `:2222` | `check_code_citations` | WARN | **(iv) NON-GRAPH** | repo Markdown × repo source files |
| `[K0]` | `:2274` | `check_links` | ERR | **(iv) NON-GRAPH** | `systems/graph/link-baseline.json` must **not** exist |
| `[K0]` | `:2331` | `check_links` | INFO | **(iv) NON-GRAPH** | — |
| `[K1]` | `:2317` | `check_links` | ERR | **(iv) NON-GRAPH †** | repo Markdown link targets |
| `[K2]` | `:2306`, `:2322` | `check_links` | ERR | **(iv) NON-GRAPH †** | repo Markdown anchors |
| `[X1]` | `:2377` | `check_relations` | ERR | **(iv) NON-GRAPH** | `systems/graph/relations.json` (existence) |
| `[X1]` | `:2405` | `check_relations` | ERR | **(iii) CROSS** | `relations.json` × **raw** `COLLECTIONS` files on disk (`:2391-2394`) |
| `[X2]` | `:2411` | `check_relations` | ERR | **(iii) CROSS** | same |
| `[X4]` | `:2425` | `check_relations` | WARN | **(iii) CROSS** | same |
| `[X6]` | `:2436` | `check_relations` | ERR | **(ii) GRAPH** | — |

**† one qualification that matters, and it cuts against the module's design note.** `check_links` (`:2280-2295`) walks `REPO` pruning only `_is_transient` and `archive/`. It does **not** skip `systems/views/`, whereas `DOC_SKIP` (`:1289`) and `ID_SKIP` (`:1306`) both do. So `[K0]`/`[K1]`/`[K2]` from `check_links` read the **generated views as ordinary input**. That makes them (iv) with respect to the graph but partly **(i)-fed**: any broken link inside a view is an error the regenerator itself authors, and an empty graph renders link-free views, so that share of `[K1]`/`[K2]` is silenced by the same act that empties the graph. I report this; I propose nothing.

**Totals by class (counting (code, function) pairs, 89 rows above):** (i) VIEW **2**; (ii) GRAPH **35**; (iii) CROSS **28**; (iv) NON-GRAPH **24**.

### R2 — Why only three families survived, stated as a mechanism (`PRIMARY`, source reading; the 123/89/18/16 counts are W37b's execution, not re-run by me)

Emptying the graph and regenerating splits the census three ways:

- **(i) VIEW (2 families)** — `[G1]`/`[G2]` dissolve **by construction**: `check_views` `:4535-4547` compares each file against `all_views(g)`, the exact string `write_views` `:4524` just wrote. This is the escape in its pure form.
- **(ii) GRAPH (35 families)** — go silent **without needing the regenerator at all**. Every one is `for row in g[coll]`; zero rows, zero iterations. Emptying alone buys these.
- **(iii) CROSS (28) and (iv) NON-GRAPH (24)** — the only families that can still fire. Of the CROSS families, **direction decides**: a family that fires on *"present in the other home, absent from the graph"* survives (`[L2]`, `[M2]`, `[W1]`); a family that fires on *"present in the graph, absent from the other home"* goes vacuous with everything else (`[L4]`, `[M3]`, `[W2]`, `[S1]`–`[S3]`, `[B4]`, `[P1]`/`[P2]` in `check_pointers`, `[X2]`/`[X3]`/`[X5]` in `check_scan_interop`).

That is the complete explanation of W37b's 123, and it also predicts the **error** subset exactly: the only ERROR-severity families that both survive emptying *and* are affected by it are `[L2]`, `[M2]`, `[W1]`. The (iv) NON-GRAPH families — `[D4]` above all — fire at the same rate before and after and are the campaign's own baseline, which is why W37b's green-baseline manoeuvre (moving the campaign directory outside the scan root) was necessary before any of this was interpretable.

### R3 — ⭐ The answer to the hazard question: which families become escapable, and the exact ownership change (`PRIMARY`, source reading)

`write_views` `:4524-4532` owns exactly one path prefix: `systems/views/`. Three ownership widenings would each convert one surviving family into an escapable one, because the regenerator would then author **both sides** of the comparison:

| Ownership change | Families that become escapable | ERRORs removed from W37b's 123 |
|---|---|---|
| **A.** A graph→legacy writer: `all_views`/`write_views` (or a new `--write-legacy`) gains authority over `research/manuscripts/emc-systems-map.json` — i.e. the legacy registry becomes *rendered from* `g` rather than hand-maintained | `[L1]`, `[L2]`, `[L3]`, `[L4]` (`check_legacy_agreement` `:1060-1103`) | **89** → 34 remain |
| **B.** A graph→roadmap writer: the module (or `extract_requirement_register.py` inverted) gains authority over the **R\* register table in `research/manuscripts/nr4a3-program-map.md`** | `[M1]`–`[M5]` (`check_requirement_source_agreement` `:1180-1223`) | **16** → 18 remain |
| **C.** A lane-register writer, or equivalently adding the repository sweep's roots to the regenerator's output set, so the `LANE-n` mentions and `systems/graph/lanes.json` share one author | `[W1]`, `[W2]` (`check_lanes` `:1126-1147`) | **18** → **0 remain: exit 0 over 0 objects** |

**A alone removes 72% of the surviving errors. A+B+C makes `systems_check.py --check` exactly as escapable as `emc_systems_map_check.py` — W37's generalisation would then cover the whole navigational surface.** Note the asymmetry of the risk: **A is the cheap one and the dangerous one.** `[L2]` is 89 of 123 by itself, and the legacy registry is the only one of the three whose other home has *no* generator at all (below), so "let's generate it, it is already derived data" is the plausible-sounding change that would do the most damage.

**Concretely: what already exists, and in which direction (`PRIMARY`).** `systems/extract_requirement_register.py` exists and its docstring says it was written *because* `[M4]` named a remedy that did not exist. It writes `systems/graph/requirements.json` **from** `nr4a3-program-map.md` (`REPO/…/nr4a3-program-map.md` → `systems/graph/requirements.json`, `--write`, `:112-114`), and its docstring states the invariant explicitly: *"THE ROADMAP IS THE SOURCE, ALWAYS. … This tool never writes in the other direction."* So change **B** is **the inversion of an existing tool's stated invariant**, not a new tool — which is exactly the shape of change that gets made by accident during a convenience refactor. `systems/extract_plan.py` runs the same direction (`SRC = research/manuscripts/nr4a3-program-map.md` → `OUT = systems/graph/plan.json`, `:14-15`). For change **A** there is **no writer at all**: `grep -rn "emc-systems-map" --include=*.py --include=*.mjs --include=*.sh` finds only `emc_systems_map_check.py --write-view` `:1326`, which regenerates the **`.md` view** from the JSON — the JSON itself is hand-maintained, and that hand-maintenance is the whole reason `[L2]` survives.

### R4 — Two escapes that need no ownership change at all (`PRIMARY`, source reading; incidental, reported without a repair)

While reading `main()` I found that the (i) VIEW pair can be silenced today, without emptying anything:

1. `main()` `:4568` — `if not a.no_view_check and not a.write_views: check_views(g, f)`. **`--write-views --check` in a single invocation runs the invariants but skips `check_views` entirely.** W37b's result came from two separate commands, which is why `[G2]` appeared in its first histogram at all; one command would have shown 0 `[G1]`/`[G2]` without writing a byte of comparison.
2. `--no-view-check` `:4555` is a first-class documented flag that removes the same pair.

Both are pre-existing, both are presumably deliberate, and neither affects the 123. I record them as part of the anchor census because a family's escapability is a property of the *invocation* as well as of the anchor, and I author no change to either.

**`--write-views` also skips `check_schemas`** in the sense that it writes before any check runs (`:4560-4563`, returning 0 when `--check` is absent) — W09h is credited with that finding per W37b; I did not re-derive it and do not claim it.

## Validation evidence

**RUN.** All commands executed in `/home/user/Rare-cancers` (cwd), container `container_0166QEHnXrRA8nCR59c9UG4k`, `python3` = `/usr/local/bin/python3` (stdlib `ast`/`re` only), no network.

- Start/end state: `date -u`; `git rev-parse HEAD` (`408b676a…` → `7a100267…`); `git status --porcelain` (0 lines both times); `git diff --name-only 408b676a 7a100267 | grep -v opus-capacity-campaign-20260908 | wc -l` → **`0`**, exit 0 — the HEAD move touched nothing I read.
- `wc -l systems/systems_check.py` → **`4591`**.
- `grep -n -o -E '\[[A-Z][0-9]+\]' systems/systems_check.py | … | sort | uniq -c` → 72 distinct code literals with occurrence counts (`[P1]` 14, `[B1]` 8, `[K1]`/`[K2]`/`[D8]` 7 each, …).
- `/tmp/claude-0/w37c/map.py` (ast + regex): every `[Xn]` literal → line → enclosing top-level `def`, 232 output lines. `/tmp/claude-0/w37c/io.py`: every filesystem/path-constant site → enclosing function. `/tmp/claude-0/w37c/cls.py`: per-`check_*` function summary of `g[...]` use, `VIEWS` use, path constants, repo-reading helpers, and raised codes — the 30-row table this census is built on. All three exited 0; all three deleted.
- Raise sites and surrounding blocks read directly: `:1-80`, `:180-200`, `:480-540`, `:1112-1180`, `:1289-1360`, `:1440-1444`, `:1481-1520`, `:1528-1534`, `:2061-2120`, `:2248-2300`, `:2377-2440`, `:2441-2476`, `:4502-4591`.
- Direction of the existing extractors: `sed -n '1,60p' systems/extract_requirement_register.py` (docstring: *"THE ROADMAP IS THE SOURCE, ALWAYS … never writes in the other direction"*; `--write` at `:114`); `grep -n "^OUT\|^SRC" systems/extract_plan.py` → `SRC = research/manuscripts/nr4a3-program-map.md`, `OUT = systems/graph/plan.json`.
- Absence of a legacy-registry writer: `grep -rn "emc-systems-map" --include=*.py --include=*.mjs --include=*.sh . | grep -iE 'open\(|"w"|write|dump'` → **one line**, `emc_systems_map_check.py:1326  --write-view … regenerate emc-systems-map.md`.
- Scratch deletion: `rm -rf /tmp/claude-0/w37c` then `ls` → `No such file or directory`; `df -h /` → 17 G free, 55%.

**PROPOSED (NOT RUN).** Deliberately not executed, and therefore **UNKNOWN**: the coordinated multi-file emptying W37b named as its successor (empty `systems/graph/*.json` **and** `emc-systems-map.json` **and** the roadmap R\* register together, then regenerate both modules). My census **predicts** it drives the surviving 123 to 18 (`[W1]` only) — that is a `PREDICTION` from source reading, not a measurement. I also did not run `systems_check.py` at all, in either mode.

## Limitations

- **This is a gate-behaviour census, not a scientific one.** No claim here touches EMC biology, efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab.
- **Static reading only.** I ran no `--check`, so every count in R2/R3 that carries a number (123, 89, 18, 16) is **W37b's executed measurement, cited, not re-derived by me**. My contribution is the anchor classification and its consequences; if W37b's histogram were wrong, my A/B/C arithmetic inherits the error.
- **"Families" are ambiguous by construction and I chose a unit.** Nine codes are raised from two different functions against different anchors, so a "72 codes" answer and an "89 (code, function) pairs" answer are both defensible. I report both and classify the pairs.
- **Severity is from the raise method, not from an execution.** A family classed CROSS may in practice never fire on the committed graph; nothing here asserts any current defect in the repository's graph content.
- **Two anchors I did not fully trace.** `check_artifacts`'s `ARTIFACT_DIRS` walk and `_lane_verdict_for` were read at their call sites, not line by line through `:2120-2195`; and `check_documents`' `_instruction_paths`/`_pinned_targets` were classed from their docstrings and raise sites (`:1368-1420`, `:1904`) rather than a full trace. Their class assignment (iv/iii) is high-confidence but not exhaustively verified.
- **Line numbers are live-checkout numbers at `408b676a`.** Per W38b this file is line-shifted against the frozen corpus; resolving these `:NN` in the corpus reads unrelated code.
- **I describe a hazard; I authored no repair, no patch, no gate, no test, and I weakened nothing.** R4's two invocation escapes are reported exactly as found. Whether any of changes A/B/C is desirable is a maintainer's decision, and the module's own note at `:1436` is the reason a worker should not make it.

## Stop condition

Set up front: **return the moment every `[Xn]` literal in the file has been mapped to its raise site and an anchor class by source reading, and the specific ownership change for each surviving family is named from the source rather than inferred.** Both met — 89 (code, function) pairs classified from raise sites; changes A, B, C named, with the direction of the two existing extractors read out of their own source and the absence of a legacy-registry writer measured by grep. **MET.** Returned early rather than executing the multi-file emptying, which is W37b's named successor and a different unit.

## Tool-call and wall-clock count actually used

**13 tool calls** (5 of them parallel pairs). Wall clock **04:38:48Z → 04:41:35Z ≈ 2 min 47 s** — well inside the ~40-call / ~40-minute target.

## Next concrete action

**One successor, inside this lane: measure R3's prediction rather than leave it as a prediction.** On a scratch copy whose baseline is first established as rc=0 (campaign directory moved outside the scan root, per W31b/W37b), empty the 15 `COLLECTIONS` **and** `research/manuscripts/emc-systems-map.json` **and** the `**R<n>**` rows of the roadmap register together, then `--write-views` and `--check`. My census predicts **18 ERROR, all `[W1]`**; W37b measured 123 with only the graph emptied. If the count lands on 18, the ownership hazard is quantified end-to-end and the gate's true remaining depth is the filesystem `LANE-n` sweep alone — the single anchor no generator can plausibly claim, and therefore the one that should never be given one. That is a single bounded run.

**Explicitly not a successor:** any change to `write_views`' ownership, to `main()`'s `--write-views`/`--no-view-check` conditional, or to `check_links`' view-inclusion. Those are the hazard, not the fix, and authoring one is precisely what `systems_check.py:1436` warns against.
