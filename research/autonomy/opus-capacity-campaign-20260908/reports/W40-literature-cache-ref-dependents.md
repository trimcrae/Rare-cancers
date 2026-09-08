<!-- collected 2026-09-08T03:52:11Z by campaign coordinator; agent id a6e5d0ab9ed200d68; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a6e5d0ab9ed200d68.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W40** — ref-state and dependency-surface lane, OPUS-CAPACITY-CAMPAIGN-20260908. Successor to W29b/W29d/W03g on the shared `origin/literature-cache` finding.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in this container's environment names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 03:46:34 UTC 2026` · **end**: `Tue Sep  8 03:49:00 UTC 2026`.

`git rev-parse HEAD` **start**: `606d79f96526b651f3b825190d721f6b302c032e` · **end**: `e5d60db79f9dcbe7a4b2e6b0db1de6e32ccf69e7`. HEAD moved under me (the coordinator collecting sibling reports). Every finding is anchored to a `file:line` read at the live checkout or to a git query whose answer is a property of `.git` (refs/objects/reflog), which the intervening report-collection commits do not touch.

`git status --porcelain` **start**: empty · **end**: empty. No repository write, no git write operation, **no fetch**, no network, no paid API, no GPU. Scratch `/tmp/claude-0/w40/` deleted (`ls` → `No such file or directory`, quoted in Validation).

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start-of-run; the five long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` are filtered from this paste — they carry no model information):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
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
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
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

Three lanes disagree about the tree's own state and four lanes depend on the same ref. (1) **What literature-cache refs actually exist in this checkout, and is `216bd1b5fb25…` a real object here?** W29b reported `refs/heads/literature-cache` present at that SHA; W29d found neither ref and recorded the discrepancy unresolved. (2) **What is the ref's full dependency surface** — every consumer, its missing-ref behaviour (loud / announced-degrade / silent), and whether it sits on a gate path. (3) **What is actually computed from a zero-record cache today, and does it say so?**

Open because no worker has resolved the ref-state contradiction, and because every prior measurement enumerated a single consumer (W29b, W03g) or four (W29d) without asking how many there are.

## Prior-work check

```
grep -rn 'literature-cache' --exclude-dir=.git --exclude-dir=opus-capacity-campaign-20260908 .   -> 258 files
grep -rn 'literature-cache' --include='*.py' --include='*.sh' --include='*.mjs' --include='*.yml' ...
grep -rn '216bd1b5' --exclude-dir=.git .
```

`216bd1b5` appears in **exactly three places in the tree, all campaign reports** (W29b ×2, W29d ×1) — i.e. no tracked repository artifact records that SHA. Per the corrected brief, sibling reports are not repository evidence, so the SHA has **no** tracked provenance. Tracked prior art on the ref itself is plentiful (`scripts/regenerate_aso_chain.sh:50,243,320`; `submission_citations.py:137,166`; `.github/workflows/fetch-literature.yml`), but **no tracked artifact enumerates the consumer set** — that is what was missing. `CLOSED-WORK.md` closes nothing about this ref. W25 was not read, opened or referenced.

## Method and inputs

Live checkout `/home/user/Rare-cancers` only. The frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/` was deliberately **not** used: it is a file snapshot with `"contains_git_history": false`, and this question is about `.git` state, which a file snapshot cannot answer.

1. **Ref forensics, read-only:** `git for-each-ref`, `git show-ref`, `.git/packed-refs`, `find .git/refs -type f`, `.git/FETCH_HEAD`, `.git/ORIG_HEAD`, `git reflog --all`, `find .git/logs -type f`, `grep -rn literature .git/logs/`, `git cat-file -t`, `git rev-parse --verify -q`, `git cat-file --batch-check`, `ls .git/objects/21/6bd1b5*`, `git rev-parse --is-shallow-repository`, `git count-objects -v`, `git config remote.origin.fetch`.
2. **Output-format forensics** on W29b's quoted command, by running `git branch -a --list '*main*'` and `git show-ref main` in the same tree and comparing formats.
3. **Consumer enumeration:** the greps above, then reading each code consumer's missing-ref path at source (`sed -n`), plus the chain steps (`grep -n run_step`) and the CI/gate rows (`.github/workflows/tests.yml`, `scripts/preflight.sh`).
4. **Artifact inspection:** `python3 -c` reads of the committed JSON outputs for the honesty markers each producer emits (`UNREAD`, `ABSENT`, `without_fetched_metadata`, `counts`).
5. **One module execution:** `submission_citations.py --check`, after reading `main()` at `:371-470` and confirming `--check` is an `elif` **after** the `--write` branch, so it opens no file for writing. `scripts/preflight.sh` was **not** run. `research/modalities/atr_hrd_sarcoma_series.py` was **not** invoked.

## Result

### R1 — The ref's state, resolved (`PRIMARY`, executed)

| Question | Answer | Evidence |
|---|---|---|
| Does `refs/remotes/origin/literature-cache` exist? | **NO** | `for-each-ref` = 5 refs; `rev-parse --verify -q` rc=1 |
| Does `refs/heads/literature-cache` exist? | **NO** | same; `find .git/refs -type f` = 5 files; **`.git/packed-refs` does not exist**, so loose refs are the complete set |
| Is `216bd1b5fb25a56b90ef3cc2373e1fe68322708f` in the object store? | **NO — absent, not merely unreferenced** | `git cat-file -t` → `fatal: Not a valid object name`, rc=128; `git cat-file --batch-check` → **`216bd1b5… missing`**; `ls .git/objects/21/6bd1b5*` → no such file |
| Does the reflog show it ever existed and was deleted? | **NO — zero trace** | `grep -rn -i 'literature' .git/logs/` → **no output**; `.git/logs` holds exactly 5 ref logs + `HEAD`, none for literature-cache; `reflog --all` is 100% campaign report-collection commits |

**The five refs (verbatim, `git for-each-ref`, rc=0):**
```
refs/heads/claude/confident-bardeen-ji76cd            606d79f9…  commit
refs/heads/main                                       9f861f51…  commit
refs/remotes/origin/claude/confident-bardeen-ji76cd   606d79f9…  commit
refs/remotes/origin/codex/opus-cloud-inputs-20260908  ba8b66ea…  commit
refs/remotes/origin/main                              92abbcb9…  commit
```

**This confirms W29d and does not support W29b's local-ref claim, and I can say why (`PRIMARY`, format forensics).** W29b attributes this output to `git branch -a --list '*literature-cache*'`:

```
216bd1b5fb25a56b90ef3cc2373e1fe68322708f	refs/heads/literature-cache
```

**`git branch -a --list` cannot emit that.** Measured in this same tree:

```
$ git branch -a --list '*main*'          $ git show-ref main
  main                                   9f861f51… refs/heads/main
  remotes/origin/main                    92abbcb9… refs/remotes/origin/main
```

`git branch` prints two-space-indented short names with no SHA. The `<40-hex>\t<full refname>` shape W29b quoted is the output format of **`git show-ref` or `git ls-remote`** — and `show-ref` is excluded, because `show-ref` reads the same local ref store that is measurably empty of it and would have to have been recorded in `.git/logs` and `.git/refs`. `git ls-remote` queries the **remote over the network** and writes nothing locally, which fits every observation: the branch exists **on `github.com/trimcrae/Rare-cancers` at `216bd1b5…`**, and has never existed in this checkout.

**Grade this precisely.** That the command was `ls-remote` is a **STRONG INFERENCE from output format**, not a `PRIMARY` observation — I cannot read W29b's transcript, and I am forbidden to fetch, so I cannot confirm the remote branch's SHA. What is `PRIMARY` is the disjunction: **either** W29b's quoted command label is wrong (and the SHA describes the remote, not this tree), **or** a local ref existed and was deleted leaving no reflog entry, no loose ref, no packed-ref and no object — which is not a state git produces by any ordinary operation, since `git branch -D` writes a reflog line and leaves the object. **The first is the supported reading; the second is effectively ruled out by the reflog and object evidence.** Either way, **no local ref was lost between W29b's HEAD and mine** — nothing regressed, and W29d's "neither exists" is the correct description at both HEADs.

**One further measured fact nobody has recorded: this checkout is SHALLOW.** `git rev-parse --is-shallow-repository` → `true`; `.git/shallow` pins 42 grafted commits; `remote.origin.fetch` = `+refs/heads/*:refs/remotes/origin/*`. A shallow clone with a narrow initial fetch is a sufficient and ordinary explanation for the ref's absence — this is a normal cloud-sandbox checkout, not a damaged one.

### R2 — The dependency surface (`PRIMARY`, source-read; grades as stated)

258 files mention `literature-cache`; the overwhelming majority are **provenance strings inside committed JSON/Markdown** (`"read_from": "literature-cache: …"`), which are records of where a value came from and are **not consumers**. The consumers that actually resolve the ref at runtime are these:

**A. Modules that shell out to git for the ref (11 sites, 9 modules)**

| Module / line | What it reads | Missing-ref behaviour | Gate path? |
|---|---|---|---|
| `research/manuscripts/build_reference_list.py:42,78-79` | every `_index.json` on the branch, for reference metadata | **LOUD** — `sys.exit("cannot read origin/literature-cache — run \`git fetch origin literature-cache\` first")` | **No** — not a `run_step` in `regenerate_aso_chain.sh`, not in `tests.yml`/`preflight.sh` |
| `research/manuscripts/journal_reference_authors.py:111,246-255` | Europe PMC + Crossref fetch products | **LOUD** — `check=True` → `SystemExit("… \`git fetch origin literature-cache\` first")` | No (`--build` only) |
| `research/manuscripts/aso_delivery_routes.py:52,100,173` | delivery-route corpora | **ANNOUNCED DEGRADE** — `_load()` returns `None`, artifact records *"not present on the literature-cache branch at read time — an ABSENT reading"* | No |
| **`research/manuscripts/submission_citations.py:304,307`** | **every fetched record on the branch, keyed by PMID** | **SILENT** — no `check=`, `returncode` never read; `out = {}` | **YES — three of them** (below) |
| `research/manuscripts/aso_priorart_evidence.py:50,86` | the two prior-art corpus indexes | **LOUD** — prints `REFUSED: … Fetch it first: git fetch origin literature-cache:refs/remotes/origin/literature-cache`, returns `None` → **exit 2** | **YES** — `regenerate_aso_chain.sh:319` |
| `research/manuscripts/endpoint_corpus.py:47,75-92` | CTG payloads; tries **three** refs `("origin/literature-cache","literature-cache","FETCH_HEAD")` | **ANNOUNCED (at the extract boundary)** — `_payload` returns `(None,None)`; `--extract` is not gated but the default path prints `::error::no inputs cache -- run --extract first (needs the literature-cache branch)`, **return 1** | `tests.yml:204` runs `--check`, which reads the **committed** `endpoint-corpus-inputs.json`, not the branch — branch-independent today |
| `research/modalities/emc_model_junction_evidence.py:74-88` | UCSC NR4A3 RefSeq blob | **LOUD, with a docstring that states the principle** (*"A MISSING REF IS A REFUSAL, NEVER AN EMPTY LIST"*) — tries both refs, then attempts `git fetch … --depth=1`, then `RuntimeError`. **Note: this is the one consumer that issues a network git write on the missing path.** | No |
| `research/modalities/emc_prior_art_fulltext_screen.py:34,58-67` | full texts under the branch corpus | **LOUD** — `SystemExit(f"{BRANCH} is not in the local object store. Run: git fetch origin literature-cache")`, plus a second `SystemExit` if the listing is empty | No |
| `research/modalities/cd248_precedent.py:52,285-311` (reused by `alcam_precedent.py`) | Europe PMC `_index.json` | **ANNOUNCED DEGRADE, by design** — returns `_status:"UNREAD"` and *"An absent reading, not a reading of absence. No count is claimed."* Its docstring explicitly forbids a second reader that could turn this into a zero. | No |

**B. Prerequisite probes and chain wiring**

| Site | Role |
|---|---|
| `scripts/regenerate_aso_chain.sh:320` | `git rev-parse --verify -q refs/remotes/origin/literature-cache` as the prior-art step's prereq probe — **measured rc=1 now**. Probe fails + check fails ⇒ `UNCHECKABLE HERE` ⇒ `blocked` non-empty ⇒ **chain exit 3** (W03g R3) |
| `scripts/regenerate_aso_chain.sh:243` | prints the exact remedy and prices it `$0, seconds` |
| `scripts/regenerate_endpoint_chain.sh:9,20` | documents that it deliberately does **not** run `--extract`, because extraction needs the branch |

**C. Path-argument consumers (no git, no silent zero)**

`research/modalities/v18_lysine_reference_precheck.py` (`--corpus-root` a checkout/export of the branch; a missing index yields *"…not on literature-cache yet. An ABSENT reading, not an absence"*), `scripts/emc_km_reachability_census.py:41,134` (`--cache <path>`, `check=False` recording `None` = unknown), `scripts/emc_km_admissibility.py:195` (`--commit` provenance string only), `research/modalities/nr4a3_intron2_cryptic_exon.py:68` (`ENSEMBL_FETCH_DIR`), `scripts/triage-literature.mjs:7-8` (documentation comment only — **no `child_process` use**, consistent with W29d's zero `.mjs` subprocess sites).

**D. Producer** — `.github/workflows/fetch-literature.yml:659-736` is the only thing that **writes** the branch, and it is the one place the missing ref is handled as a normal state: `git fetch origin literature-cache || true`, then `if git show-ref --verify --quiet refs/remotes/origin/literature-cache; then git checkout -B … else git checkout --orphan literature-cache`. `enumerate-drugs.yml:7` names it only as the model of a branch Pages never serves.

**E. Tests** — `research/manuscripts/tests/test_submission_citations.py:120-146` is the sharpest artifact in the whole surface: it **monkeypatches `S._literature_cache = lambda: {}`** — i.e. it asserts every citation resolves *with the cache empty*, precisely because "CI is a plain checkout, and the record lived on a branch it does not have". `research/modalities/tests/test_s4_lanes.py:88-104` pins a blob SHA (`b542818379d6aedada98ab9600d4b081a65bbaef`) against the branch copy but reads it from the committed artifact, so it does not need the ref. `tests/test_wetlab_contracting_costs.py:34` and `test_emc_radiotherapy_contradiction.py:150` assert only that provenance strings *name* the branch.

**Summary of the four-way contrast, now a nine-way one:** of nine git-resolving consumers, **six fail loud, two degrade and say so in the artifact, one is silent.** W29d's framing survives enlargement: the silent one is a single omission inside a pattern this repository otherwise applies **eight times out of nine**.

### R3 — What is computed from a zero-record cache today, and what says so (`PRIMARY`, executed + artifact inspection)

| Artifact / verdict | Computed from a zero-record cache? | Does it say so? |
|---|---|---|
| `submission_citations.py --check` verdict — **`tests.yml:222`, `preflight.sh:849`, and `regenerate_aso_chain.sh:295`** | **The cache contributes 0 records to `load_meta()`, silently, on every one of those three runs.** Measured now: `74 annotated citation(s), 53 distinct PMID(s), 0 UNANNOTATED, 0 without fetched metadata / citation numbering is current`, **rc=0** | **NO.** Nothing on either stream mentions the branch (W29d's V3: 0 records, 0 bytes stdout, 0 bytes stderr) |
| `aso/fusion-junction-aso-submission-references.json` (the `--write` output of that same chain step at `:295`) | **Not yet** — the committed copy has `n_references: 53`, `without_fetched_metadata: []`. But `:295` carries **no prereq probe**, so a `--write` here regenerates it with the cache contributing nothing, silently | **NO, and worse:** its committed `_provenance` string names *"the ASO reference corpus, the curated citation maps, and the literature-cache branch"* as its sources. On this machine the third contributes zero and the file would still say it |
| `regenerate_aso_chain.sh --check` overall verdict | Not computed — **refused**, exit 3 at `:474` (W03g R3), because `:320`'s probe returns rc=1 (re-measured: rc=1) | **YES** — `INCOMPLETE (missing prerequisites)` |
| `aso/fusion-junction-aso-priorart-evidence.json` | **No.** Committed with real counts: `4252 + 1133`, `in_both 232`, `unique 5153`, `agrees_with_manuscript: true`. A regeneration here refuses at exit 2 | **YES** (refuses rather than writing) |
| `research/modalities/cd248-precedent.json`, `alcam-precedent.json` | **No** — inspected: neither contains `UNREAD`, so both hold real counts from a run that could read the corpus | **YES** if regenerated here (`_status: "UNREAD"`) |
| `aso/aso-delivery-evidence-2026-08.json` | **No** — inspected: **0 occurrences of `ABSENT`**, so it was built with the corpora readable | **YES** if regenerated here |
| `endpoint/endpoint-corpus.json` / `-inputs.json`, `tests.yml:204` | **No** — `--check` reads the committed inputs file, never the branch | n/a |

**The honest consequence, stated exactly.** Today the material harm is **zero**, for the reason W29b already gave and I re-measured: `without_fetched_metadata` is empty because the records were moved into the repository on 2026-08-17, and `_literature_cache()` is applied **last** in `load_meta()` with `if p not in out`, so it is a last-resort fill that currently fills nothing. What is real is **the mechanism, plus one thing no prior report named**: `submission_citations.py --write` sits on the chain at `:295` with **no prerequisite probe**, unlike the prior-art step at `:319-320` which has one — so the repository already knows how to gate a step on this ref and does so for one consumer and not the other. And its committed output's provenance sentence asserts a source that, on any machine in this checkout's condition, supplied nothing.

## Validation evidence

Environment: `/home/user/Rare-cancers`, Linux, system `python3`, git as installed. All **RUN**.

**V1 — ref/object/reflog forensics** (each rc quoted):
```
$ git for-each-ref --format='%(refname) %(objectname) %(objecttype)'   rc=0  -> the 5 refs in R1
$ git show-ref                                                          rc=0  -> same 5
$ cat .git/packed-refs                    cat: .git/packed-refs: No such file or directory
$ find .git/refs -type f                  -> 5 files, none literature-cache
$ git cat-file -t 216bd1b5fb25            fatal: Not a valid object name 216bd1b5fb25   rc=128
$ git rev-parse --verify -q 216bd1b5fb25                                                rc=1
$ echo 216bd1b5fb25a56b90ef3cc2373e1fe68322708f | git cat-file --batch-check
  216bd1b5fb25a56b90ef3cc2373e1fe68322708f missing
$ ls .git/objects/21/6bd1b5*              ls: cannot access …: No such file or directory
$ grep -rn -i 'literature' .git/logs/     [no output]
$ find .git/logs -type f                  -> 5 ref logs + HEAD, none literature-cache
$ git rev-parse --is-shallow-repository   true      ($ wc -l .git/shallow -> 42 grafts)
$ git config --get-all remote.origin.fetch   +refs/heads/*:refs/remotes/origin/*
$ cat .git/FETCH_HEAD    92abbcb9…  branch 'main' of https://github.com/trimcrae/Rare-cancers
$ cat .git/ORIG_HEAD     92abbcb905cacf07f14b238db50d1b98f6590374
$ git count-objects -v   count: 428  in-pack: 55678  packs: 4  garbage: 0
```

**V2 — output-format disproof of the `git branch` attribution:**
```
$ git branch -a --list '*main*'        $ git show-ref main
  main                                 9f861f51afdf23f541d80c7ef41fcb2c6953efa6 refs/heads/main
  remotes/origin/main                  92abbcb905cacf07f14b238db50d1b98f6590374 refs/remotes/origin/main
```

**V3 — the chain's prereq probe, re-measured at my HEAD:**
```
$ git rev-parse --verify -q refs/remotes/origin/literature-cache ; echo $?
1
```

**V4 — the gate verdict, executed (write path audited first: `--check` is an `elif` after `--write` at `:425-460`; it opens no file for writing):**
```
$ python3 research/manuscripts/submission_citations.py --check
74 annotated citation(s), 53 distinct PMID(s), 0 UNANNOTATED superscript(s), 0 without fetched metadata
  citation numbering is current
rc=0
$ git status --porcelain     [no output]
```

**V5 — committed-artifact inspection** (`python3 -c` JSON reads): `cd248-precedent.json` / `alcam-precedent.json` → `UNREAD` **False** in both; `aso-delivery-evidence-2026-08.json` → `grep -c ABSENT` = **0**; `fusion-junction-aso-priorart-evidence.json` → `counts.per_corpus` = 4252 / 1133, `unique_records` 5153, `agrees_with_manuscript` true; `fusion-junction-aso-submission-references.json` → `n_references` 53, `without_fetched_metadata` `[]`.

**V6 — write isolation and scratch deletion:**
```
$ rm -rf /tmp/claude-0/w40 && ls -d /tmp/claude-0/w40
ls: cannot access '/tmp/claude-0/w40': No such file or directory
$ git status --porcelain    [no output, start and end]
```

**PROPOSED (NOT RUN):** confirming the remote branch's tip SHA (needs `git ls-remote`/`fetch` — **forbidden, network, not attempted**); executing the six loud consumers to observe their exit codes here; running `regenerate_aso_chain.sh` end to end. **No repair, patch, diff, gate or test was authored, proposed as code, or applied.** `scripts/preflight.sh` not run. `atr_hrd_sarcoma_series.py` not invoked. `submission_citations.py`'s defect was left with the module's owner, per dispatch.

## Limitations

- **I cannot prove the remote branch exists at `216bd1b5…`.** Fetching is forbidden. That SHA's meaning is **UNKNOWN** to this measurement; my inference names it as *most likely* a remote tip read by `ls-remote`. An absent reading is not a reading of absence — I have not shown the branch does not exist upstream, and every piece of tracked evidence (`fetch-literature.yml`'s publish step, the 5,153-record prior-art artifact) is consistent with it existing and being healthy.
- **The `ls-remote` attribution is an inference from output format, not an observation of W29b's command.** Its transcript was not available to me. What is measured is that no local literature-cache ref, reflog entry or object exists here.
- **"No local ref was lost" is a claim about *this* checkout's `.git`.** If W29b ran in a different container or a differently-cloned tree, that tree's state is UNKNOWN to me.
- **The 258-file mention count is not 258 consumers.** I classified consumers by reading code; the provenance-string majority was classified by file type and spot reads, not by reading all 258. The nine git-resolving modules were each read at source. A consumer that resolves the ref by some route I did not grep for (an env var, an indirect helper) would be missed — the enumeration is a thorough screen, not a proof of completeness.
- **Gate-path membership was checked against `tests.yml`, `preflight.sh` and the two regenerate chains only.** Other workflows were not read; membership elsewhere is UNKNOWN.
- **Only one module was executed.** The eight other consumers' behaviour here is read from source, not demonstrated, exactly as graded.
- Nothing here concerns EMC efficacy, safety, selectivity, therapeutic window or clinical readiness, and no patient data was touched. This is a version-control and software-dependency finding. There is no wet lab.

## Stop condition

**Set up front:** return once (a) the literature-cache ref state is settled with local heads, remote-tracking refs, packed-refs, reflog, object presence and shallow status all measured, and the W29b/W29d discrepancy is either resolved or its irreducible unknown named; (b) every consumer of the ref across `scripts/`, `research/`, `systems/`, `.github/workflows/` and the regenerate chains is enumerated with its missing-ref behaviour and gate-path status; and (c) the zero-record consequence is stated per artifact, distinguishing what says so from what does not.

**MET.** (a) R1 — neither ref exists, the object is `missing`, the reflog has zero trace, the checkout is shallow, and the discrepancy is resolved in favour of W29d with the format disproof; the remote's tip remains honestly UNKNOWN. (b) R2 — nine git-resolving consumers plus probes, path-argument consumers, the producer workflow and three tests, each graded. (c) R3 — one silent consumer on three gate paths, one un-probed `--write` chain step, and no committed artifact currently holding a zero-record result. Returned immediately.

## Tool-call and wall-clock count actually used

**16 tool calls** (all `Bash`; no repository write, no git write, no fetch, no network, no paid API, no GPU, no background task). **Wall clock 03:46:34Z → 03:49:00Z ≈ 2.5 minutes** of execution, plus report drafting, against the ~40-call / ~40-minute target. Returned early.

## Next concrete action

**One bounded successor for this lane, for the PUB-ASO owner and the coordinator jointly.** The chain already contains the pattern the fix needs: `regenerate_aso_chain.sh:319-320` gives the prior-art step a `git rev-parse --verify -q refs/remotes/origin/literature-cache` prereq probe, and `:243` prints the remedy. The **submission references** step at `:295` has no probe, and it is the step whose `--write` output carries a provenance sentence naming the branch. The successor should decide — **as one decision, not two** — whether `:295` gets the same probe that `:319` already has, and it should be taken together with the `submission_citations.py:304,307` disposition W29d routed to the module's owner, because a probe at the chain and a `returncode` check in the module solve overlapping halves of one problem and landing either alone leaves the other invisible. I am not the actor: my dispatch forbids authoring the repair, `CLAUDE.md` §7 puts a chain-step change with one coordinator in an isolated worktree, and W29d already placed the module half with its owner.

**Second, smaller, and available to any read-only worker:** W29b's `216bd1b5…` line should get a one-sentence focused correction (per `CORPUS-CONTEXT.md` §4, a correction, not a re-review) recording that the quoted command label does not match the quoted output format and that no local ref ever existed here — otherwise a future reader treats "the branch was here and vanished" as a repository incident, which it measurably is not.
