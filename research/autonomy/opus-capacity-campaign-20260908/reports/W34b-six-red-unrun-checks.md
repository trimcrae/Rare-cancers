<!-- collected 2026-09-08T03:49:31Z by campaign coordinator; agent id a071e27580aa9d492; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a071e27580aa9d492.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W34b** — verification-mode reachability lane (successor to W34), OPUS-CAPACITY-CAMPAIGN-20260908. Scratch `/tmp/claude-0/w34b/`, deleted before returning (`ls -d` → `No such file or directory`; free 20G).

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My context states Opus 5, exact ID `claude-opus-5`. No environment variable in this container names a served model; the coordinator must extract the actual runtime model from the transcript.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:40:07 UTC 2026` | `Tue Sep  8 03:44:36 UTC 2026` |
| `git rev-parse HEAD` | `5ae0fa04ff9516ac8f820381079d644a094f4a77` | `606d79f96526b651f3b825190d721f6b302c032e` |
| `git status --porcelain` | **empty (0 lines)** | **empty (0 lines)** |

HEAD moved under me (the coordinator is landing sibling reports). Verified nothing I measured changed: `diff -rq --exclude=.git --exclude=__pycache__ /home/user/Rare-cancers /tmp/claude-0/w34b/tree` returned **only** campaign-directory entries — one changed `COMMON-BRIEF.md` (the 03:36Z correction) and eight `Only in …/reports:` lines (`W03g`, `W06i`, `W18c`, `W29c`, `W29d`, `W35b`, `W36`, `W38`). **Not one byte under `research/modalities/`, `research/manuscripts/`, `systems/` or `scripts/` differs.** I wrote nothing into the repository and ran no git write operation.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (piped through `cut -c1-90`; long proxy/truststore lines truncated, none names a model):

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

## Question

W34's named next action, exactly: **for each of the six unrun-and-red `--check` modes, plus the UNKNOWN seventh, which of three is it — (a) the committed artifact is stale relative to its generator, (b) an input artifact changed and the consumer's stamp is behind, or (c) the generator is not reproducible in this container?** With the specific evidence: differing keys, stamped-vs-current hashes, and where the changed input came from. And two hypotheses to test: are `emc_mtap_locus_persample` + `emc_prmt5_multiplicity` + `emc_mtap_prmt5_figures` one cause with three symptoms, and do `alcam_precedent` + `cd248_precedent` share one cause?

Open because W34 explicitly did not diagnose any red, and could not run `cd248_precedent.py` meaningfully on a `.git`-less copy.

## Prior-work check

Read in full: `COMMON-BRIEF.md` (including the 03:36Z correction and the "Known, measured, and NOT worth rediscovering" section), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W34-unrun-check-census.md`, `reports/W16g-unmeasured-panel-consumers.md`. `W16f` was located and sized (297 lines) but read only through W16g's reproduction of it — a stated limitation. **W25 not read, not referenced.**

Commands run for provenance:

```
git log -1 --format='%h %ad %s' --date=short -- <each of 8 artifacts>   # all 14a3f172 2026-09-04
git log --oneline -- research/modalities/emc-expression-panels.json | wc -l   # 1
git rev-list --count HEAD                                              # 349
git log --format='%h %p' | tail -3                                     # 14a3f172 has no parent
git for-each-ref --format='%(refname)'                                 # 5 refs, no literature-cache
git remote -v                                                          # origin only
```

**Not replaying:** I did not re-derive W16g's identity measurements (`38233b8e…` / `123bd05a…`, the seven-member cluster, the `surface-address-sensitivity.json` parent SHA) — I reproduced the two figure-stamp hashes only because they are the direct evidence for my own diagnosis, and they agree exactly. No GSE re-reading, no registry work, no ICD-O, no NR4A Perspective under any framing, no patient or oligonucleotide design work, no publication act. **No network initiated.** No content-policy refusal encountered.

## Method and inputs

Read-only. `tar --exclude=./.git --exclude='*/__pycache__'` copy of HEAD `5ae0fa04` to `/tmp/claude-0/w34b/tree` (612 MB). Python 3.11.15 (`/usr/local/bin/python3`), stdlib + the repository's own numpy dependency, `PYTHONDONTWRITEBYTECODE=1`. `scripts/preflight.sh` NOT run; `PREFLIGHT_FULL` NOT set.

For every module I read its `--check` dispatch in source and confirmed it returns before any `open(…, "w")` / `json.dump(…, open(…, "w"))` **before running it**. `alcam_precedent` and `cd248_precedent` were the only two run in the live tree — they need `.git`, and both provably return at the `--check` branch ahead of the single `json.dump(res, open(OUT, "w"), indent=2)` at `cd248_precedent.py:449` / `alcam_precedent.py:334`. Everything else ran in the scratch copy. `atr_hrd_sarcoma_series.py` was never invoked.

Diagnosis instrument: two scratch scripts (`deep.py`, `deep2.py`) that import the module, call its own `compute()`/`build()`/`derive()`/`stamp()`, and recursively leaf-diff the result against the committed artifact — the same comparison the module's `--check` makes, but reporting the differing leaf paths and values instead of only the top-level key names.

## Result

### R0 — The controlling fact about provenance · PRIMARY

**Git history cannot answer "where the changed input came from" for any of these artifacts.** The repository is 349 commits deep on a **squashed root**: `14a3f172` has no parent, and every one of the eight artifacts I examined has `git log --oneline -- <file> | wc -l` = **1**, all at `14a3f172` (2026-09-04). Every state change discussed below happened **before** the squash and is invisible to `git log`. All provenance below is therefore read from artifact **content** — internal timestamps, generator-stamped content hashes, and re-derivation — not from history. Category (b) is established by content stamps, never by a commit.

### R1 — All seven diagnosed · PRIMARY

| Rank | Module | Category | Cause, in one line |
|---|---|---|---|
| 1 | `emc_mtap_prmt5_figures.py` | **(b)** | Its figure-provenance stamp is behind 2 of its 4 inputs; the other 2 hashes match exactly. |
| 2 | `emc_mtap_locus_persample.py` | **(b)** | Built from the `2026-08-09` panel; the committed panel is `2026-08-29` and carries more genes. |
| 3 | `emc_prmt5_multiplicity.py` | **(b)** | Same panel growth, reaching FWER-adjusted p-values. |
| 4 | `alcam_precedent.py` | **(c)** | `origin/literature-cache` is not a ref in this checkout, so the corpus reads UNREAD. |
| 5 | `emc_fusion_frame_figure.py` | **(b)**, a **different** cluster | Its stamp is behind **all 3** of its inputs — the Ensembl-fetched construct chain, not the panel. |
| 6 | `aso_control_oligos.py` | **none of the three — a fourth category** | The committed artifact was **hand-corrected after generation**; the generator still emits the pre-correction text. |
| 7 | `cd248_precedent.py` (W34's UNKNOWN) | **(c)** — **RESOLVED** | Identical cause to #4; red in a tree *with* `.git` too. |

### R2 — Ranks 1-3 are one cause with three symptoms · PRIMARY — hypothesis CONFIRMED

The single cause is `research/modalities/emc-expression-panels.json`, which grew.

`emc_mtap_locus_persample --check` reports `DRIFT in: ['_generated_from', 'per_platform']`. The leaf diff (**200 of 1287 leaves differ**) shows exactly what `_generated_from` is: `emc_mtap_locus_persample.py:299` sets it to `panels.get("generated_utc")`.

```
._generated_from: committed='2026-08-09T18:41:04+00:00' -> now='2026-08-29T12:51:32+00:00'
```

`2026-08-29T12:51:32+00:00` is verbatim the `generated_utc` of the committed `emc-expression-panels.json`. **That leaf alone proves category (b): the consumer's artifact was built from a panel twenty days older than the one committed beside it.**

The remaining 199 leaves are all one shape — the panel simply contains more genes now:

| Quantity | committed | now |
|---|---|---|
| `array_dimness_panel_cache.<GSM>.n_genes_read`, GSE24369/GPL6244 (×35 samples) | 404 | 464 |
| `array_dimness_wide_cache.n_genes_in_cache`, GSE24369 | 1857 | 2284 |
| `array_dimness_wide_cache.n_genes_in_cache`, GSE4303/GPL3290 | (see below) | — |
| `cache_merge.n_symbols_panel_cache`, GSE24369 (from `emc_prmt5_multiplicity`) | 1857 | 2284 |
| `cache_merge.n_symbols_panel_cache`, GSE4303/GPL3290 | 1662 | 2035 |

Grouped, the 200 differing leaves in `emc_mtap_locus_persample` are **`._generated_from` (1)** plus **199 under `per_platform.*.controls_on_the_candidate_set.array_dimness_{panel,wide}_cache.*`** — array-quality control diagnostics only. **No headline scientific leaf moved**: no MTAP or CDKN2A percentile, no candidate list, no `n_deletion_consistent_tumours`, no binomial bound, no within-EMC Spearman. That is decision evidence for the owner; it is not my decision.

`emc_prmt5_multiplicity --check` reports `DRIFT in: ['per_platform']`, **42 of its leaves**, and here the drift **does** reach the results, because the panel is the multiple-testing family:

| Platform | `family_size_genes` | PRMT5 FWER *p* | MAT2A | CDKN2A | NR4A3 |
|---|---|---|---|---|---|
| GSE24369 committed | 5449 | 0.2081 | 0.9782 | 0.5084 | 0.8498 |
| GSE24369 now | **5770** | **0.2135** | 0.9810 | 0.5198 | 0.8572 |
| GSE4303-GPL3290 committed | 4848 | 0.2376 | 0.9653 | — | — |
| GSE4303-GPL3290 now | **5103** | **0.2473** | 0.9704 | — | — |

The direction is what a larger family predicts (every adjusted *p* rises). No conclusion flips — all are far from any threshold — but the committed numbers are not the numbers the current inputs produce. **UNKNOWN, and outside my scope: whether any of these committed *p*-values is quoted in manuscript prose.**

`emc_mtap_prmt5_figures --check` is the third symptom. Its stamp compares content hashes of four artifacts; **two match byte-for-byte and two do not:**

| source artifact | stamped | now |
|---|---|---|
| `emc-expression-panels.json` | `38233b8ebf557d48` | **`123bd05a9f9f5d08`** |
| `census-route-expression-grading.json` | `a21cdbebdda19710` | **`5bc3c80c034dde77`** |
| `depmap-sarcoma-dependency.json` | `d88bed62a80dcb51` | `d88bed62a80dcb51` (**match**) |
| `emc-prmt5-substrate-motif-map.json` | `12f6cf2c2764c2d6` | `12f6cf2c2764c2d6` (**match**) |

**Two of four matching is itself the diagnosis.** A timestamp, a git revision, a network read or a dict ordering would perturb all four or none. Two exact matches and two exact mismatches is a changed *input*, not an irreproducible *generator*.

**The direction is one-way, and I measured it:** `python3 research/modalities/emc_expression_panels.py --check` → **`REPRODUCES`, rc 0**, offline, in this container. The committed panel is exactly what its own generator produces from its committed cached inputs. So the panel is self-consistent and the three consumers are behind it; the panel is not itself a stale side of the disagreement. **I am not deciding which side is stale** — the owner may legitimately choose to hold the consumers and revert the panel — but the panel's self-consistency is a measured fact and belongs in that decision.

**Where the panel's change came from:** `emc_expression_panels.py` derives offline from `emc-expression-panels-inputs.json` plus signature sets whose Enrichr/MSigDB fetch diagnostics are recorded in the artifact (`ChEA_2022` 757 terms, `GO_Biological_Process_2025` 5343, `Reactome_Pathways_2024` 2105, `TF_Perturbations_Followed_by_Expression` 1958, all `ok: true`). The panel's own `_what` records the enlargement: *"plus (2026-08-07) the surface-antigen read that five blocked routes turn on."* So the panel grew by an added read, in a networked CI run, and the consumers were never re-derived. **UNKNOWN:** I did not attribute the 404→464 growth to specific added symbols; the enlargement is measured, its exact composition is not.

### R3 — Same cluster as W16g, seen from the runner side · PRIMARY

**Yes, ranks 1-3 are W16g's cluster, and rank 1 is literally W16g's seventh member.** My independently reproduced `38233b8e… → 123bd05a…` is byte-identical to W16g's. W16g reached the cluster by regenerating consumers and diffing leaves; I reached it by asking which unrun `--check` exits non-zero. **The two routes converge on the same artifacts and neither found a member the other missed within the panel family.** W34's rank-1/2/3 (`emc_mtap_prmt5_figures`, `emc_mtap_locus_persample`, `emc_prmt5_multiplicity`) are three of W16g's seven; W16g's other four (`emc_proteostasis_read`, `emc_prmt5_route_controls`, `emc_hypoxia_confounds`, `emc_prmt5_effect_sizes`) are absent from W34's red list because W34 only ran the never-invoked set — those four are invoked by some runner and so were never in W34's population at all.

**The compounding statement the two reports make together:** the panel-drift cluster is seven artifacts, and at least three of them are guarded by a `--check` that is red today and that **no runner has ever executed**. The drift was measurable at any commit for weeks and nothing was looking.

**Ranks 5-6 and 4/7 are NOT this cluster.** They are three further, independent causes.

### R4 — Ranks 4 and 7 are one cause with two symptoms · PRIMARY — hypothesis CONFIRMED

`alcam_precedent.py:43` does `import cd248_precedent as CD248` and calls `CD248._corpus_index(CORPUS_DIR)` — the module's own docstring says the reader has **one home** on purpose, so that a second reader cannot turn an unreadable corpus into a zero. Both modules therefore fail at the same line, `cd248_precedent.py:302`:

```python
raw = subprocess.run(["git", "show", f"{CORPUS_REF}:{corpus_dir}/_index.json"], cwd=ROOT, ...)
```

with `CORPUS_REF = "origin/literature-cache"` (`cd248_precedent.py:52`).

**Measured in the live tree, which has `.git`:**

```
$ python3 research/modalities/alcam_precedent.py --check   → DRIFT in: ['emc_specific_evidence']   rc=1
$ python3 research/modalities/cd248_precedent.py --check   → DRIFT in: ['emc_specific_evidence']   rc=1
$ git show origin/literature-cache:literature/cd248-binder/_index.json
fatal: invalid object name 'origin/literature-cache'.
$ git for-each-ref --format='%(refname)'
refs/heads/claude/confident-bardeen-ji76cd
refs/heads/main
refs/remotes/origin/claude/confident-bardeen-ji76cd
refs/remotes/origin/codex/opus-cloud-inputs-20260908
refs/remotes/origin/main
```

The differing key resolves to exactly one thing:

| | committed | recomputed here |
|---|---|---|
| `alcam-precedent.json._status` | `READ`, `n_retrieved=6547`, `n_on_topic=657`, `n_EMC_mentioning=0` | **`UNREAD`** |
| `cd248-precedent.json._status` | `READ`, `n_retrieved=1643` | **`UNREAD`** |

**Category (c), unambiguously: the committed artifacts were generated in CI where `origin/literature-cache` was fetched, and this checkout has only five refs, none of them that branch.** This is a container-capability difference, not artifact drift. **W34's UNKNOWN for `cd248_precedent` is resolved: it is red in a tree with `.git` as well, and for a reason `.git` alone does not fix.**

The module is behaving exactly as designed — its docstring calls this "FAIL-HONEST" and refuses to report the count as zero — so the red is the guard working, not the guard broken. But note the shape for the owner: **this `--check` cannot pass in any checkout that has not fetched `literature-cache`**, which means wiring it into a runner would make the gate depend on a branch fetch. That is a reason it is currently unwired, whether or not it was the intended one. **UNKNOWN: whether `origin/literature-cache` exists on the remote at all** — I did not fetch, and absence locally is UNKNOWN, not absence.

### R5 — Rank 5 is a second, independent stamp cluster · PRIMARY

`emc_fusion_frame_figure.py:269` prints `STALE`, and the stamp comparison it does not print is:

| source artifact | stamped in `emc-atr-figure-provenance.json` | now |
|---|---|---|
| `emc-construct-inputs.json` | `a561b8bb534d4148` | **`9166e09ec8e9d0bb`** |
| `emc-fet-construct-designs.json` | `31117a8ac40755a5` | **`726aae02ae38b41c`** |
| `emc-fet-frame-and-composition.json` | `b8b52dc3085ff4c0` | **`eb92812555c9239c`** |

**All three drifted, and none of the three is `emc-expression-panels.json`.** This is a separate chain: `emc-construct-inputs.json` is the Ensembl gene-model fetch cache written by `emc_fet_construct_designs.py fetch_inputs` (`emc_fet_construct_designs.py:94,101`), and the other two are derived from it (`emc_fet_frame_and_composition.py:53`).

Direction, measured: `emc_fet_frame_and_composition.py --check` → **`REPRODUCES`**. So the committed `emc-fet-frame-and-composition.json` is current with respect to its own generator and its inputs, and **the figure's stamp is what is behind** — category (b), origin an Ensembl re-fetch, cascading through two derived artifacts into a figure nobody redrew. `emc-fusion-frame-fig1.png` and `.pdf` are both committed. The module's own `write_provenance` docstring anticipated this exactly: *"A number changed in an artifact and not redrawn is a stale figure, and the fix is to redraw it, never to re-stamp."*

Incidental, outside my six and **not diagnosed**: `emc_fet_construct_designs.py --check` in the same run reported `DRIFT in: ['gene_models', 'ensembl_vs_uniprot_sequences']`. That module is network-dependent (it is one of W34's six Ensembl timeouts), so its drift here is confounded with blocked egress and I make no claim about it.

### R6 — Rank 6 is a fourth category, and it is the one that must not be "fixed" by re-running · PRIMARY

`aso_control_oligos.py --check` compares the **full serialized text** of a fresh `build()` against the committed file and prints `aso-control-oligos.json is stale; re-run without --check`. That message is wrong about the direction, and the leaf diff shows why. Of **38 committed leaves, exactly 2 differ**, and **every sequence, seed, draw count and duplex measurement reproduces exactly**:

| leaf | committed | generator emits now |
|---|---|---|
| `.⛔_not_a_claim_of_inertness` | *"A control here is a sequence that **CLEARS** the same specificity screen the reagent clears, matched on length, terminal bases, base composition and dinucleotide counts. … ⛔ THIS FIELD SAID 'FAILS' UNTIL 2026-08-30 AND WAS THE DIRECT INVERSE OF `_what` IN THE SAME OBJECT … Found by round 22's arithmetic seat."* | *"A control here is a sequence that **FAILS** the specificity screen the reagent passes …"* |
| `._superseded_not_a_claim_of_inertness` | the old "FAILS" text, retained as a superseded record | **`<ABSENT>`** |

Plus a serialization difference: the committed file is written with **2-space indent**, the generator emits **`indent=1`** (`len(cur)=3206` vs `len(new)=1997`), which is what makes the byte comparison fail across every line.

**So this is neither (a), (b) nor (c). The committed artifact is AHEAD of its generator: a documented scientific correction dated 2026-08-30 was applied to the artifact by hand and never carried back into `aso_control_oligos.py`.** The generator source still contains the inverted caveat. ⭐ **Consequence for the owner, stated plainly: obeying this module's own error message — "re-run without `--check`" — would silently revert a recorded caveat-direction correction and delete the `_superseded_…` record of it.** The artifact's own text says the inversion is *"the caveat-to-overclaim inversion shape, sitting green in an artifact rather than in prose — `lint_claims` cannot see it."* Re-running would put it back. **I did not repair this and am not proposing the repair; the smallest correct fix is a generator edit, and that is the module owner's call.**

### R7 — What this says about wiring · PRIMARY

Reinforcing W34's instruction and my own: **do not wire any of these seven into a runner.** Beyond the six that would turn the gate red, ranks 4 and 7 would additionally make the commit gate depend on a `literature-cache` branch fetch, and rank 6's error message actively advises the destructive action. Four distinct causes sit behind seven reds; three of them (the two stamp clusters and the hand-correction) need an owner decision before any guard is armed, and one (the corpus ref) needs an environment guarantee, not a code change.

## Validation evidence

Environment for every command: Linux 6.18.44-fc-v24 x86_64, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Python 3.11.15, `PYTHONDONTWRITEBYTECODE=1`, **no network initiated**. Scratch tree from HEAD `5ae0fa04`.

**RUN**

| # | Command (cwd) | Exit | Key output |
|---|---|---|---|
| 1 | `tar --exclude=./.git --exclude='*/__pycache__' -cf - . \| (cd …/tree && tar -xf -)` | 0 | `COPY_OK` |
| 2 | `git log -1 …` ×8 artifacts; `git log --oneline -- <f> \| wc -l` | 0 | all `14a3f172 2026-09-04`; all counts **1** |
| 3 | `git rev-list --count HEAD`; `git log --format='%h %p' \| tail -3` | 0 | `349`; `14a3f172` has **no parent** |
| 4 | `deep.py emc_mtap_locus_persample.py` (scratch) | 0 | `committed_leaves=1287 recomputed_leaves=1287 differing=200`; `._generated_from: '2026-08-09T18:41:04+00:00' -> '2026-08-29T12:51:32+00:00'` |
| 5 | `deep2.py emc_mtap_locus_persample.py` (grouped) | 0 | 1 × `_generated_from`; 199 × `array_dimness_{panel,wide}_cache`; **TOTAL 200** |
| 6 | `deep2.py emc_prmt5_multiplicity.py` (scratch) | 0 | **TOTAL 42**, all under `per_platform` |
| 7 | inline: family sizes and adjusted *p* (scratch) | 0 | `5449 -> 5770`; `4848 -> 5103`; `PRMT5 0.2081 -> 0.2135`, `0.2376 -> 0.2473` |
| 8 | `python3 research/modalities/emc_expression_panels.py --check` (scratch) | **0** | **`REPRODUCES`** |
| 9 | `python3 research/modalities/emc_mtap_prmt5_figures.py --check` (live, non-writing per `:445-460`) | **1** | both DRIFT lines verbatim as in W34; stamp vs `_fingerprint()` table in R2 |
| 10 | `python3 research/modalities/alcam_precedent.py --check` (live) | **1** | `DRIFT in: ['emc_specific_evidence']` |
| 11 | `python3 research/modalities/cd248_precedent.py --check` (live) | **1** | `DRIFT in: ['emc_specific_evidence']` |
| 12 | `git show origin/literature-cache:…/_index.json`; `git for-each-ref`; `git remote -v` | — | `fatal: invalid object name 'origin/literature-cache'`; 5 refs, none is it |
| 13 | inline: committed `_status` vs `emc_specific_evidence()` now (live) | 0 | `READ`(6547/657/0) and `READ`(1643) → both **`UNREAD`**, verbatim `⛔ CORPUS UNREAD — git show … failed` |
| 14 | inline: `emc_fusion_frame_figure.stamp()` vs committed `sources` (live) | 0 | **3 of 3 DRIFT**, hashes in R5 |
| 15 | `python3 research/modalities/emc_fet_frame_and_composition.py --check` (scratch) | 0 | **`REPRODUCES`** |
| 16 | `python3 research/modalities/emc_fet_construct_designs.py --check` (scratch) | — | `DRIFT in: ['gene_models','ensembl_vs_uniprot_sequences']` — **confounded with blocked network, not diagnosed** |
| 17 | inline: `aso_control_oligos.build()` text + leaf diff (scratch) | 0 | `byte-identical: False len_cur 3206 len_new 1997`; **38 vs 37 leaves, 2 differing**; committed indent = 2 |
| 18 | `git status --porcelain \| wc -l` (live, end) | 0 | **0** |
| 19 | `diff -rq --exclude=.git --exclude=__pycache__ /home/user/Rare-cancers /tmp/claude-0/w34b/tree` | 0 | only `COMMON-BRIEF.md` + 8 `Only in …/reports:` lines — **nothing under `research/`, `systems/`, `scripts/`** |
| 20 | `rm -rf /tmp/claude-0/w34b; ls -d …; df -h /` | — | `No such file or directory`; free 20G |

**PROPOSED (NOT RUN)** — stated explicitly, none of it performed:
- Fetching `origin/literature-cache` and re-running ranks 4 and 7. Not run: it is a network act my brief prohibits.
- Re-running `emc_fet_construct_designs.py` with Ensembl reachable, to separate its drift from blocked egress.
- Redrawing either figure (needs `matplotlib`; and redrawing writes into the tree).
- Any repair, patch, gate, test or wiring change. **I authored none, and propose none as code.**
- Deciding which side of any drift is stale. **Not done — the data owner's call, as W16f and W16g both left it.**

## Limitations

- **Git history is blind here (R0).** Every artifact entered at a squashed root, so "an input artifact changed" is established from artifact content and stamped hashes, never from a commit. The *date* of any change is only as good as the timestamp inside the artifact.
- **`emc_expression_panels.py --check` reproducing means the panel is self-consistent with its committed cached inputs.** It does **not** mean the panel is correct, nor that the 2026-08-29 regeneration was intended. Self-consistency is one input to the owner's decision, not the decision.
- **I did not verify that `origin/literature-cache` exists on the remote.** Locally absent is UNKNOWN, not absent.
- **The `emc_prmt5_multiplicity` *p*-value shifts are measured; their manuscript exposure is not.** I did not check whether any committed adjusted *p* is quoted in prose or pinned in `pinned-figures.json`.
- **`aso_control_oligos`' 2-space committed indent is consistent with a hand edit but does not prove one** — a prior generator version could have used `indent=2`. The caveat-text inversion and the `_superseded_…` record are the load-bearing evidence, not the whitespace.
- **W16f read only through W16g's reproduction of it.** Anything in W16f that W16g did not carry forward is outside my coverage.
- **This is a tooling and file-consistency audit.** Nothing here is a scientific result. A red `--check` on an MTAP/PRMT5 artifact means an artifact and its generator disagree about a gene-set size; **it says nothing whatever about EMC biology, efficacy, safety, selectivity, therapeutic window or clinical readiness.** There is no wet lab. A transcript percentile is an ASSOCIATION, never a mechanism.

## Stop condition

**Set before any measurement:** return the moment (1) each of the six reds plus `cd248_precedent` carries a category verdict with its differing keys or stamped-vs-current hashes; (2) both of W34's shared-cause hypotheses are tested and answered yes or no with evidence; (3) the W16g-cluster question is answered from the runner side without re-deriving W16g's identity measurements; and (4) the live tree is proved untouched.

**MET, all four.** (1) seven verdicts, four distinct causes, one of them outside W34's three-way taxonomy; (2) both confirmed — ranks 1-3 share `emc-expression-panels.json`, ranks 4 and 7 share one `_corpus_index` at `cd248_precedent.py:302`; (3) yes, same cluster, rank 1 is W16g's seventh member, and the two reports' independent routes converge; (4) `git status` empty at both ends and the `diff -rq` shows only coordinator files. Returning immediately rather than extending into the repair, which is owner work.

## Tool-call and wall-clock count actually used

**22 tool calls** (all `Bash`; one background). **Wall clock `03:40:07Z → 03:44:36Z` = 4 min 29 s** of measurement, plus report drafting. Well inside the ~40-call / ~40-minute target; returned on meeting the stop condition. One call ran in the background (the 612 MB scratch copy) while I read source, per `CLAUDE.md` §2.

## Next concrete action

**One finite task, and it is a report to a named owner, not a repair:** put the R6 finding in front of the owner of `research/modalities/aso_control_oligos.py`, because it is the only one of the seven where the *published instruction is destructive*. The module prints `aso-control-oligos.json is stale; re-run without --check`, and re-running would overwrite the 2026-08-30 caveat-direction correction (`CLEARS` → back to `FAILS`) and drop the `_superseded_not_a_claim_of_inertness` record that documents it, while all 36 substantive leaves — sequences, seed `20260824`, draw counts, duplex measurements — are already byte-equal. The smallest correct repair is a two-string edit in the generator so it emits the corrected caveat and the superseded record, plus `indent=2`; **I did not write it and do not propose it as code**, because it changes what an artifact asserts about a control reagent and that is the ASO owner's call, not a tooling worker's.

**Explicitly NOT the next action:** wiring any of the seven into a runner (four distinct unresolved causes; two would make the gate depend on a branch fetch); regenerating any committed artifact; or deciding which side of either stamp cluster is stale. The panel cluster's owner decision — hold the seven consumers or hold the 2026-08-29 panel — is now fully evidenced by W16f, W16g and this report together and needs no further measurement to be taken.
