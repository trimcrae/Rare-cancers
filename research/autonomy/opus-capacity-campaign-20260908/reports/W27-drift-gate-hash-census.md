<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:23:46Z UTC
     agent id a5d1fd67f0de5468a ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a5d1fd67f0de5468a.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

**W27** · OPUS-CAPACITY-CAMPAIGN-20260908 · tooling audit lane (successor to W20g's incidental finding).

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in this container's environment names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 03:13:33 UTC 2026` · **end**: `Tue Sep  8 03:19:41 UTC 2026`

`git rev-parse HEAD` **start**: `98a0833f1ede2cf9cef13790388260567a32e868` · **end**: `84f02dae1809ae050e40254f06310ed849982527`. **HEAD moved twice under me** (coordinator collecting other workers' reports). I checked the exposure rather than assuming it: `git diff --name-only 98a0833..HEAD -- research/modalities research/manuscripts systems` returns **0 files**. No file I measured changed during this run. Neither HEAD is the brief's frozen `92abbcb9`; I read the live checkout and additionally anchor every finding to `file:line` and to content I quote.

`git status --porcelain` **start**: 8 untracked report files under `research/autonomy/opus-capacity-campaign-20260908/reports/` (other workers' collected reports, pre-existing, not mine). **end**: `0` lines — the tree is clean and I wrote nothing into it. All execution under `/tmp/claude-0/w27/`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; the four long proxy variables — `no_proxy`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are in the transcript verbatim, contain no model information, and are marked below):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=<proxy list, no model information>
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
GLOBAL_AGENT_NO_PROXY=<proxy list, no model information>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<truststore + proxy flags, no model information>
NO_PROXY=<proxy list, no model information>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<proxy list, no model information>
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

## Stop condition (set up front, before any measurement)

**Stop when: (1) every non-test module under `research/modalities` and `research/manuscripts` implementing `--check` is enumerated and its drift comparison classified from source; (2) for every module whose comparison is narrower than "everything it publishes", the published set and the compared set are given with `file:line` on both sides, in both directions; (3) at least three published-but-not-gated values are demonstrated on a scratch copy by mutation + a real `--check` exit code, with the scratch restored between demonstrations and the live tree untouched; (4) the gaps are ranked by what a wrong value reaches; (5) the repair is priced against the measured `commit-loop` headroom without proposing a ceiling increase.**

**MET.** All five done; (3) was exceeded — **five** demonstrations, all real exit 0. Returning immediately.

---

## Question

W20g found incidentally that `emc_fourth_cohort_quant.py` publishes `probe_counts_sha256` but omits it from the module's `--check` drift keys, while `gene_counts_sha256` is listed. **How general is that gap? Across every module under `research/modalities` and `research/manuscripts` that implements a `--check` drift comparison, what is the set difference between what the module PUBLISHES into its committed artifact and what its `--check` actually COMPARES — and what does a wrong value in the difference reach?**

Open because W20g measured one module and explicitly deferred the generalisation ("a smaller related gap… adding it is a one-line change"), and because neither W13f (cross-file *pool-flag* coverage) nor W17h (Welch *block* coverage) measured the **within-module** publish-vs-gate difference. W17h's headline — 99.2 % of committed inferential statistics is unreachable by any gate — makes the question sharper, because `--check` is the mechanism most of these modules present as their reproducibility guarantee.

---

## Prior-work check

| Command | What it showed |
|---|---|
| Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W20g-published-denominator-consistency.md`, `reports/W13f-cross-file-gate-coverage.md`, `reports/W17h-welch-coverage-census.md` | W20g §3 tail is the seed and is **not replayed**: I do not re-derive the 662/77/211,362 split, do not re-run the k-histogram, and do not author its label repair. W13f measures *cross-file* registry-flag coverage — a different axis. W17h measures *statistical-block* coverage and identifies `test_aso_delivery_antigen.py` as the one gate-reachable Welch check; my D4 below is a **different** object (the committed artifact's own `controls` block vs `--check`), and I say so explicitly. |
| `grep -rln -- '--check' research/modalities research/manuscripts` | 268 paths including prose; narrowed by AST/source reading to **130 non-test `.py` modules** that actually define or dispatch on `--check`. |
| `git ls-files 'research/modalities/*.py' 'research/manuscripts/**/*.py'` + per-file source read of the `--check` block | the census in R1. |
| `git grep -l "<artifact-stem>" -- ':!research/autonomy'` for each gap artifact | the reach ranking in R4. |

**CLOSED-WORK items confirmed not replayed**: no NR4A Perspective, no Brenca/Hofvander/Pazopanib/Sunitinib/Wagner/CTARC route, no GSE4303/GSE28866 re-reading, no registry ICD-O work, no patient or specimen identity work, no source fetch. **No network was used deliberately.** One incidental note for the record: `aso_delivery_antigen.py --check` itself attempted two outbound connections to `www.ebi.ac.uk:443` during my run; both were **`connect_rejected` by the egress proxy**, the module tolerated the failure and still exited 0. I did not initiate, retry, reroute or work around that; I report it because it happened under my command. No content-policy refusal was encountered. The frozen corpus at `/tmp/claude-0/frozen-corpus/` was not needed — every claim here is about code at the recorded live HEADs.

---

## Method / inputs

**Inputs.** All 130 non-test `.py` modules under `research/modalities` and `research/manuscripts` that define or dispatch on `--check`; their committed output artifacts; `scripts/tier_budget.py` and `scripts/tier-budgets.json`.

**Tools.** Python 3.11 stdlib only (`json`, `re`, `os`, `subprocess`, `shutil`, `ast`-free regex extraction), `git`, `grep`, `tar`. No third-party package, no network request initiated, no GPU, no paid API.

**My scratch code**, all under `/tmp/claude-0/w27/`: `scan.py` (extracts each module's `--check` block by indentation), `classify.py` (classifies the comparison idiom), `demo.py` (the mutation harness). Nothing was written into the repository.

**Scratch copy and write isolation.** `tar -cf - --exclude=./.git . | (cd /tmp/claude-0/w27/scratch && tar -xf -)` → 611 MB, plus `pristine.tar` (626,462,720 bytes) as the restore baseline. Every `--check` was executed with `cwd=/tmp/claude-0/w27/scratch`, never in `/home/user/Rare-cancers`. Each demonstration restores its artifact from the live tree before and after mutating.

**Per-module `--check` write-hazard inspection — required by the dispatch, done for every module I ran, before running it.** I read each `--check` code path in source and confirmed it `return`s before any `open(..., "w")`, `os.replace` or `json.dump` to disk:

| Module | Source inspection before running | Ran? |
|---|---|---|
| `nurr1_allosteric_vs_pocket5.py` | `:762-769` builds in memory, compares, `return`s; the two writes are at `:770-774`, after the check's return | **RAN** (scratch) |
| `gse11185_wt_vs_fusion.py` | `:913-919` compares and returns; writes at `:921-925` | **RAN** (scratch) |
| `aso_delivery_antigen.py` | `:833-844` compares and returns; write at `:845` | **RAN** (scratch) |
| `emc_tissue_read_statistics.py` | `:425-427` prints and returns; write at `:429` | **RAN** (scratch) |
| `nr4a3_acceptor_numbering.py` | `:146-155` reads `OUT`, prints, returns; write at `:157` | **RAN** (scratch) |
| `emc_prior_art_fulltext_screen.py` | `:126-128` prints and returns; write at `:130` | **RAN** (scratch) — exits 1 here for an unrelated missing git ref, see Validation |
| **`emc_fourth_cohort_quant.py`** | `:928` calls `derive()` **unconditionally, before** the drift comparison at `:934-941`; `derive()` writes `PROBE_TSV` (`:817`) and `GENE_TSV` (`:829`). **Confirms W20g's reading.** Even on the scratch copy it additionally requires phase caches I did not attempt to build | **NOT RUN — `PROPOSED (NOT RUN)`** |
| `gse243553_eno3_overlap.py` | `:1677-1686` reads `RECON_OUT` and prints; no write | not run (finding is from source; no comparison exists to demonstrate against) |

After all demonstrations, `tar -df pristine.tar -C scratch .` reported **no content differences** (only metadata lines, filtered), and the live tree's `git status --porcelain` was **0 lines**.

---

## Result

### R1 — Census: 130 modules, classified by what their `--check` actually compares (`PRIMARY`)

| Class | n | What the `--check` does |
|---|---|---|
| **A — compares NOTHING** | **6** | Re-reads (or recomputes) and *prints*; returns 0 unconditionally. Gated set = ∅. |
| **B — compares a PARTIAL key subset** | **4** | Compares a hand-listed subset of what it publishes. |
| **C — compares the whole document** | 42 | `cur != new` on bytes, or `json.load(OUT) != out`, or every top-level key. Published set = gated set (at top level). |
| **D — delegates to a `check()` function** | 22 | `return check()`; **not individually inspected** — see Limitations. |
| **E — unclassified by my extractor** | 56 | 40 with a block my idiom-matcher did not resolve, 16 where no `args.check` line exists (the flag is consumed inside a helper). **Not asserted either way.** |

**The good news first, and it is real: the dominant idiom is a whole-document comparison.** 42 modules compare their entire committed output byte-for-byte or key-for-key, so for them the published-but-not-gated set is empty by construction. The W20g gap is **not** the general case. It is a **10-module class** (A + B), and within that class it is severe.

### R2 — Class A: six modules whose `--check` gates nothing at all (`PRIMARY`)

These are the sharpest finding, and they are worse than W20g's case: not a missing key, but a `--check` that performs **no comparison of any kind** and cannot fail.

| Module and gate `file:line` | What the gate does | Published set | Gated set |
|---|---|---|---|
| `research/modalities/nr4a3_acceptor_numbering.py:146-155` | opens its **own committed output**, prints four fields from it, `return 0` at `:155` | all of `nr4a3-acceptor-exon-numbering.json` | **∅** |
| `research/manuscripts/venue_fee_screen.py:325-332` | opens `aso/venue-fee-screen.json`, prints every `journals[].verdict`, `return 0` at `:332` | all of `venue-fee-screen.json` | **∅** |
| `research/manuscripts/nat_scope_census.py:352-361` | opens the output, prints `n_computation_only_candidates` / `n_with_abstract` / `n_indexed` and per-topic counts, `return 0` at `:361` | all of the census artifact | **∅** |
| `research/modalities/gse243553_eno3_overlap.py:1677-1686` | opens **`RECON_OUT`** (`gse243553-eno3-overlap-recon.json`, defined at `:87`), prints four keys, `return 0` at `:1686` | all of `gse243553-eno3-overlap.json` (24 top-level keys) **and** the recon file | **∅** |
| `research/modalities/emc_prior_art_fulltext_screen.py:126-128` | *does* recompute `out`, then prints `out["counts"]` and `return 0` at `:128` — never opens the committed artifact | all of `emc-prior-art-fulltext-screen.json` | **∅** |
| `research/modalities/emc_tissue_read_statistics.py:425-427` | *does* recompute, then prints a one-line summary and `return 0` at `:427` — never opens the committed artifact | all 16 top-level keys of `emc-tissue-read-statistics.json`, incl. **354 committed Welch blocks** (W17h R1) | **∅** |

The first four are **self-attestation**: the check reads the committed file and prints it back. Whatever the file says, the check says it too, and exits 0. D5 below demonstrates that literally — the check prints a value I fabricated as though it had verified it.

### R3 — Class B: four modules that compare a proper subset of what they publish (`PRIMARY`)

Published side = top-level keys of the committed artifact with its own `file:line`; gated side = the module `file:line` of the comparison.

**B1 · `research/modalities/emc_fourth_cohort_quant.py` — gate at `:938-941`** (W20g's seed, confirmed and quantified)

- Gated (5): `probe_gate`, `n_runs_read`, `n_probes_common_to_every_read_run`, `n_genes_with_at_least_one_assigned_probe`, `gene_counts_sha256` — all at `emc_fourth_cohort_quant.py:938-941`.
- **Published-but-not-gated: 22 of 27 top-level keys.** With `emc-fourth-cohort-quant.json:line`: `_title`:2, `_generated_by`:3, `_generated_utc`:4, `_inputs_generated_utc`:5, `_cost`:6, `_what_this_is_not`:7, `bioproject`:13, `sra_study`:14, `depositor_assay_description`:15, `⚠ depositor_description_is_one_source`, `n_runs_in_deposit`:46, `per_run`:48, `probe_map`:230, `gene_counts_written_to`:278, `why_no_differential_expression`:279, `sample_labels`:280, `probe_counts_written_to`:285, **`probe_counts_sha256`:286**, `probe_counts_n_rows`:287, `⛔ a_zero_in_the_probe_table`, `gene_counts_n_rows`:290, `⛔ gene_counts_units`.
- Gated-but-not-published: **none** (all 5 gated keys exist in the artifact).
- **Scale of the hole, quantified:** the ungated set contains the *entire* `probe_map` block (`:230`) — every denominator W20g audited, including `n_probes_offered`, `n_probes_assigned_to_one_gene`, `n_probes_unassigned`, and all `per_core_length` fractions — plus the whole `per_run` block (`:48`, 12 runs × read/retention/persistence counts), plus `probe_counts_sha256` and `probe_counts_n_rows`. Both TSVs are additionally *side outputs* the `--check` never compares as files; only `gene_counts_sha256` stands in for one of them.

**B2 · `research/modalities/aso_delivery_antigen.py` — gate at `:838-839`**

- Gated (2): `per_antigen`, `headline`.
- **Published-but-not-gated: 16 of 18 top-level keys.** With `aso-delivery-antigen.json:line`: `_what`:2, `_why`:3, `_execution_model`:4, `_language_discipline`:5, `_not_preregistered`:6, `_inputs`:7, `instrument_reach`:13, `scoring_rules`:142, `by_joint_verdict`:884, **`controls`:908**, `the_two_normal_tissue_instruments_where_they_disagree`:968, `hpa_vital_tissue_override_is_inert`:1069, `stage_1_coverage_over_this_universe`:1090, `what_this_changes_for_PUB_ASO`:1176, `routed_next_steps`:1195, `⛔_what_this_file_does_NOT_claim`.
- `controls:908` contains `artifact_self_consistency_recomputed_welch_t` — **the exact block W17h identified as the repository's only gate-reachable Welch verification**. The pytest gate re-derives it live from `M.derive()`; the module's own `--check` does not compare the committed copy. D4 demonstrates it.

**B3 · `research/modalities/gse11185_wt_vs_fusion.py` — gate at `:917-918`**

- Gated (2, both nested under `verdict`): `verdict.answer_2_what_it_is`, `verdict.★_answer_4_what_differs_between_wild_type_and_fusion`.
- **Published-but-not-gated: 11 of 12 top-level keys.** With `gse11185-wt-vs-fusion.json:line`: `_title`:2, `_question`:3, `_status`:4, `_inputs`:5, `characterisation`:10, `instrument_controls`:230, `read`:637, `top_divergent_probes`:749, `decision_relevant_panel`:1105, `af1_premise_bearing`:4379, `the_papers_own_conclusion`:4604 — plus every subkey of `verdict` other than the two named. The module also writes a **second output**, `gse11185-wt-vs-fusion.md` (`:923-924`), which the `--check` never compares at all.

**B4 · `research/modalities/nurr1_allosteric_vs_pocket5.py` — gate at `:766`**

- Gated (1): `verdict.answer` — a single string.
- **Published-but-not-gated: 17 of 18 top-level keys.** With `nurr1-allosteric-vs-pocket5.json:line`: `_title`:2, `_question`:3, `_status`:4, `_cost`:5, `source`:6, `paper_numbering_check`:16, `site_definition`:105, `pocket5_definition`:287, `mapping`:303, `structure_frame`:324, `comparison_full_site`:337, `★_comparison_over_the_full_deposited_ensemble`, `comparison_mutagenesis_anchored_only`:825, `control_other_epitopes_from_the_same_paper`:842, `burial`:894, `frozen_gate`:920, `source_quote_verification`:929. Also writes a `.md` sibling (`:773-774`) that is never compared.

**A correction I am recording rather than burying.** My first automated pass reported `gse243553_eno3_overlap.py` as having three *gated-but-not-published* keys. That was **my error**, not the module's: I compared its gate keys against `gse243553-eno3-overlap.json` when the gate reads `RECON_OUT` (`:87`), a different file. Reading the source corrected it to the Class A finding above. **Across all ten Class A+B modules, the true gated-but-not-published set is empty** — no module compares a key its artifact does not contain.

**The nearest real gated-but-not-published asymmetry is in Class C**, and it is minor. Two idioms coexist:
- symmetric — `drift = [k for k in res if old.get(k) != res[k]]` **plus** `drift += [k for k in old if k not in res]`: `emc_mtap_locus_persample.py:481-482`, `emc_prmt5_effect_sizes.py:571-572`.
- one-way — the first line only: `cd248_precedent.py:446` (read in source), and by the same pattern `alcam_precedent.py:326`, `aso_genome_offtarget.py:1621`, `emc_atr_vulnerability.py:3197`, `emc_expression_panels.py:2876`, `emc_prmt5_multiplicity.py:660`.
Under the one-way idiom, a key **deleted** from the derived output while still present in the committed artifact is not reported as drift. That is a stale-key hole, not a wrong-value hole, and it is one line to close in each.

### R4 — Demonstrated consequence: five mutations, five real exit 0 (`PRIMARY`, RUN)

Every run below: `cwd=/tmp/claude-0/w27/scratch`, `python3` = system Python 3.11, Linux 6.18.44-fc-v24, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, no network initiated. Exit codes are `subprocess.CompletedProcess.returncode` of the module itself — **not** a pipeline's exit status. (I caught myself reading `tail`'s exit code in a first attempt and re-ran the whole batch; the corrected run is what is reported.) The artifact is restored from the live tree before and after each demonstration.

| # | Module (gate line) | Mutation applied to the committed artifact | Baseline | **After mutation** |
|---|---|---|---|---|
| **D1** | `emc_tissue_read_statistics.py:425` (Class A) | `primary.GPL6244.ACAN`: `t` 0.529 → **99.0**, `p` 0.604454 → **0.0**, `significant` false → **true** | exit **0** | **exit 0** — `emc_tissue_read_statistics: verified, 100 board genes, 95 readable on GPL6244, 78 on GPL3290` |
| **D2** | `nurr1_allosteric_vs_pocket5.py:766` (B4) | `source_quote_verification.status`: `"OK"` → `"FABRICATED-BY-W27"` | exit **0** | **exit 0** — `[check] verdict MATCH -> MATCH : SAME` |
| **D3** | `gse11185_wt_vs_fusion.py:917` (B3) | `decision_relevant_panel._what` (prose) → `"W27-MUTATED"` | exit **0** | **exit 0** — `[check] SAME` |
| **D4** | `aso_delivery_antigen.py:838` (B2) | `controls.artifact_self_consistency_recomputed_welch_t` (the whole Welch self-consistency block) → the string `"W27-MUTATED"` | exit **0** | **exit 0** — `aso_delivery_antigen --check: per_antigen and headline reproduce exactly` |
| **D5** | `nr4a3_acceptor_numbering.py:146` (Class A) | `n_transcripts`: 4 → **99999** | exit **0** (`4 transcripts, 4 coding; …`) | **exit 0** — and the check **prints the fabricated number back as verified**: `99999 transcripts, 4 coding; first-coding-exon ranks [1, 3]; rank-2 numbering exists: False` |

D5 is the clearest statement of the defect class: the gate's output is a function of the file it is supposed to be checking, so a corrupted artifact produces a *corrupted-but-green* report. D4 is the one with the most reach: the block I replaced with a bare string is the artifact's own record that its Welch statistics re-derive from committed per-sample values, and the module's `--check` announces "reproduce exactly" over it. D3 is the weakest of the five — the key I hit is prose (`_what`), so it demonstrates the class boundary rather than a wrong number; the same gate would equally miss a wrong number anywhere in `read`, `top_divergent_probes` or `af1_premise_bearing`.

**Not demonstrated, and labelled honestly.** `emc_fourth_cohort_quant.py --check` — the module that generated the question — is **`PROPOSED (NOT RUN)`**. Its `--check` calls `derive()` unconditionally at `:928` and `derive()` writes both TSVs; I would only ever have run it on the scratch copy, and it additionally needs phase caches I did not build. Its `probe_counts_sha256` gap therefore rests on **source reading** (`:938-941` vs `:286`), exactly as W20g left it, and is **not** claimed as an executed demonstration.

### R5 — Ranking by what a wrong value reaches (`PRIMARY` for the reference map; the ranking itself is my judgement)

Reach measured by `git grep -l "<artifact-stem>" -- ':!research/autonomy'`.

| Rank | Module / artifact | Reaches | Why it ranks here |
|---|---|---|---|
| **1** | `aso_delivery_antigen.py` → `aso-delivery-antigen.json` (16/18 keys ungated) | **`systems/graph/blockers.json`**, `systems/views/registers/blockers.md`, **`research/manuscripts/aso/fusion-junction-aso-research-article.md`** (PUB-ASO, the paper CLAUDE.md §0 names as first to finish), `aso-delivery-antigen-2026-08-08.md`, `aso-delivery-evidence-2026-08.md`, `fusion-junction-aso-archive-manifest.json`, `emc-systems-map.json/.md` | the only gap artifact transcribed into **both** model state and the priority manuscript; and the ungated `controls` block is precisely the evidence a reviewer would rely on |
| **2** | `emc_fourth_cohort_quant.py` → `emc-fourth-cohort-quant.json` (22/27 keys ungated) | **`systems/graph/routes.json`**, `systems/views/L2-rt-immunocytokine.md`, `systems/views/L2-rt-fusion-output.md`, `emc-fourth-cohort-route-readout.json`, `expression-validation-readiness.json` (which pins its `file_sha256`), `.github/workflows/emc-expression-datasets.yml` (ships the probe TSV as a standalone CI artifact) | model state + two views + a shipped dataset; W20g already showed a published route conclusion resting on this file's fields |
| **3** | `gse243553_eno3_overlap.py` → `gse243553-eno3-overlap.json` (gates nothing) | **`research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md`**, `gse243553-eno3-overlap-2026-08-08.md`, `.github/workflows/emc-expression-datasets.yml` | transcribed into a manuscript; no `systems/graph/` path found |
| **4** | `nurr1_allosteric_vs_pocket5.py`, `gse11185_wt_vs_fusion.py` | `research/modalities/s4-lane-map-edits.json` + `s4_lane_map_edits.py` + `tests/test_s4_lanes.py` | feed the **map-edit** channel, which is how lane state reaches `systems/graph/`; one step further from model state than ranks 1-2, and the s4 test is some independent coverage |
| **5** | `emc_tissue_read_statistics.py` (gates nothing; 354 Welch blocks) | `research/manuscripts/figures/emc-surface-figure-provenance.json`, `surface-targets/…-review-response-2026-08-10.md` | a figure-provenance record and a review response — real transcription, but no model state and no active manuscript |
| **6** | `nr4a3_acceptor_numbering.py`, `venue_fee_screen.py`, `nat_scope_census.py`, `emc_prior_art_fulltext_screen.py` | no consumer outside their own module found | **the smallest holes**: a wrong value is read only by its own artifact. Worth fixing because they are the cheapest fixes, not because they are dangerous |

**The ordering answer the dispatch asked for:** ranks 1-2 are qualitatively different from the rest, because a wrong value there is transcribed into `systems/graph/` — the repository's own model state, which `CLAUDE.md` §7 makes authoritative — and into the manuscript queue. Rank 6 is a self-contained artifact whose only reader is itself.

### R6 — Price of the repair (I did not write it) (`PRIMARY` for the budget numbers)

Measured on the live tree, read-only, `python3 scripts/tier_budget.py`, **exit 0**:

```
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
```

**The binding constraint is stated plainly and not argued with.** The dispatch records the owner's writer-side measurement as **1497/1500** for `commit-loop`. That is the number any proposal must honour — **3 function slots**, not the 34 this cloud checkout's 1466 would suggest (W13f recorded the same source-base gap). **I do not propose raising the ceiling, and no option below requires it.**

| Option | Test-function cost | Tier impact | Honest assessment |
|---|---|---|---|
| **1. Repair the ten `--check` bodies in place** — Class A gets a real comparison; Class B widens to the whole document, i.e. adopts the idiom the other **42 modules already use** | **0** | **none — no tier budget consumed at all** | **The correct first move.** It is a within-module edit per module, needs no new test file, and cannot fail the ceiling because it adds no test function. Expect it to *surface* drift: a check that has never compared anything may go red on first honest run. That is discovery, and per `CLAUDE.md` §6 the response is to fix the drift, never to re-narrow the guard. |
| **2. Add a static meta-guard** — one test asserting every module defining `--check` compares against its committed output, plus one negative control (the repository's `test_a_guard_that_cannot_fail_is_not_a_guard.py` convention) | **2** | `commit-loop` **1497 → 1499 / 1500**. Fits, with **1 slot left**. | Feasible but it spends two thirds of the remaining headroom on one guard, and it needs an explicit allowlist for the 22 Class-D and 56 Class-E modules I did not resolve — otherwise it is a heuristic that flags what it does not understand, exactly the failure W13f reported in its own check. **Not recommended before Option 1.** |
| **3. Per-artifact runtime guards** (regenerate-and-compare tests for the ten artifacts) | ~10-20 | would go to **`modalities`** (7247/7500, headroom **253**), not `commit-loop` | Affordable in the right tier, but largely redundant with Option 1: a whole-document `--check` already *is* that comparison, and `scripts/preflight.sh` is where `--check` is exercised. |

**Recommendation, priced: Option 1 — 0 test functions, 0 tier budget, ten module edits.** If the owner also wants a guard against the class reappearing, Option 2 costs 2 of the 3 remaining `commit-loop` slots and should only be taken with the Class-D/E allowlist resolved first. Neither is authored here; both need an owner and the normal commit gate.

---

## Validation evidence

**RUN.** Environment for every command: Linux 6.18.44-fc-v24 x86_64, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, `python3` = system Python 3.11 (`/usr/lib/python3.11`), no network initiated. Repository commands run with cwd `/home/user/Rare-cancers` (read-only); all module executions with cwd `/tmp/claude-0/w27/scratch`.

1. **Scratch copy** — `tar -cf - --exclude=./.git . | (cd /tmp/claude-0/w27/scratch && tar -xf -)` → `du -sh` = **611M**; `pristine.tar` = **626,462,720 bytes**.

2. **Baseline `--check` runs, real module exit codes** (`subprocess.run(...).returncode`):
```
=== research/modalities/nurr1_allosteric_vs_pocket5.py REAL_EXIT=0
[check] verdict MATCH -> MATCH : SAME
=== research/modalities/gse11185_wt_vs_fusion.py REAL_EXIT=0
[check] SAME
=== research/modalities/aso_delivery_antigen.py REAL_EXIT=0
aso_delivery_antigen --check: per_antigen and headline reproduce exactly
=== research/modalities/emc_tissue_read_statistics.py REAL_EXIT=0
emc_tissue_read_statistics: verified, 100 board genes, 95 readable on GPL6244, 78 on GPL3290
=== research/modalities/emc_prior_art_fulltext_screen.py REAL_EXIT=1
origin/literature-cache is not in the local object store. Run: git fetch origin literature-cache
```
`emc_prior_art_fulltext_screen.py` exits **1** here for a missing local git ref, before reaching its (comparison-free) check body. Its Class-A status is a **source finding** (`:126-128`), **not** an executed demonstration. I did not fetch the ref.

3. **The five mutation demonstrations**, verbatim harness output (`/tmp/claude-0/w27/demo.py`):
```
--- D1 emc_tissue_read_statistics (--check compares nothing)
  mutation: primary.GPL6244.ACAN t=99.0, p=0.0, significant=true (was ('ACAN', (0.529, 0.604454, False)))
  BASELINE  exit=0  emc_tissue_read_statistics: verified, 100 board genes, 95 readable on GPL6244, 78 on GPL3290
  MUTATED   exit=0  emc_tissue_read_statistics: verified, 100 board genes, 95 readable on GPL6244, 78 on GPL3290
  VERDICT: STAYS GREEN — gap confirmed

--- D2 nurr1_allosteric_vs_pocket5 (gates verdict.answer only)
  mutation: source_quote_verification.status -> FABRICATED-BY-W27 (was 'OK')
  BASELINE  exit=0  [check] verdict MATCH -> MATCH : SAME
  MUTATED   exit=0  [check] verdict MATCH -> MATCH : SAME
  VERDICT: STAYS GREEN — gap confirmed

--- D4 aso_delivery_antigen (gates per_antigen+headline only)
  mutation: controls.<first welch key> -> 'W27-MUTATED'
            (was ('artifact_self_consistency_recomputed_welch_t',
                  '{"_what": "every array t used below, re-derived from the committed per-sample z values", "'))
  BASELINE  exit=0  aso_delivery_antigen --check: per_antigen and headline reproduce exactly
  MUTATED   exit=0  aso_delivery_antigen --check: per_antigen and headline reproduce exactly
  VERDICT: STAYS GREEN — gap confirmed

--- D5 nr4a3_acceptor_numbering (--check re-reads its own output and prints it)
  mutation: n_transcripts -> 99999 (was 4)
  BASELINE  exit=0  4 transcripts, 4 coding; first-coding-exon ranks [1, 3]; rank-2 numbering exists: False
  MUTATED   exit=0  99999 transcripts, 4 coding; first-coding-exon ranks [1, 3]; rank-2 numbering exists: False
  VERDICT: STAYS GREEN — gap confirmed

--- D3 gse11185_wt_vs_fusion (gates 2 verdict subkeys only)
  mutation: decision_relevant_panel.<first key> -> 'W27-MUTATED'
            (was ('_what', '"genes this repository\'s other lanes already turn on, read out of this experimen'))
  BASELINE  exit=0  [check] SAME
  MUTATED   exit=0  [check] SAME
  VERDICT: STAYS GREEN — gap confirmed
```

4. **Tier budget**, live tree, read-only: `python3 scripts/tier_budget.py` → the three lines quoted in R6, **exit 0**.

5. **Write isolation confirmed both ways.** `tar -df pristine.tar -C scratch .` after all demonstrations → **no content differences** (only mtime/uid/gid/mode lines, filtered). Live tree: `git status --porcelain | wc -l` → **0** at `03:18:58Z` and again at `03:19:41Z`; `git diff --name-only 98a0833..HEAD -- research/modalities research/manuscripts systems` → **0 files**. I ran no git write operation and did not run `scripts/preflight.sh`.

**PROPOSED (NOT RUN)**, explicitly:
- `python3 research/modalities/emc_fourth_cohort_quant.py --check` — refused by design (writes two TSVs via `derive()` at `:928`; needs phase caches). Outcome **UNKNOWN**; no drift claim made from it.
- Any repair. I authored no fix, placed no file, edited no `--check`, and touched no tier budget.
- Option 2's meta-guard. It is described and costed; **no such test was written or executed**, and no pytest run of any kind was attempted this session.

---

## Limitations

- **56 of 130 modules (Class E) are unclassified and 22 (Class D) delegate to a `check()` I did not follow.** So my census covers **52 of 130 modules with confidence**. The A+B count of 10 is therefore a **lower bound on the gap class**, not a total. Absence of a finding in Class D/E is **UNKNOWN, not proof of absence** — some of those 78 modules may have narrower gates than any I found.
- **The publish/gate comparison is at the top level of each artifact.** A Class C module comparing every top-level key is complete at that level; my method would not detect a gate that compares whole keys but whose *derive* silently drops a nested field. I make no claim about nested completeness in Class C.
- **Side outputs are under-counted.** I noted `.md`, `.tsv` and `.csv` siblings for the modules I read (`gse11185`, `nurr1`, `emc_fourth_cohort_quant`) but did not systematically enumerate every module's non-JSON outputs. There may be more uncompared side files.
- **D3's mutated field is prose, not a number.** It demonstrates the gate's blindness, not a corrupted measurement.
- **Mutating the committed artifact is one of the two routes the dispatch allowed** (artifact, or input). I chose artifact mutation because it directly models the failure mode of interest — a committed value that no longer matches what the code produces. Mutating upstream *inputs* would exercise the derive path too and might expose additional failures; I did not do that, so those outcomes are **UNKNOWN**.
- **`aso_delivery_antigen.py --check` attempted network egress and was denied.** It exited 0 anyway. Whether its comparison would behave differently with network access is **UNKNOWN**; I did not and will not test that.
- **No clinical claim of any kind.** This is an audit of exit codes in a repository. Nothing here says any committed value *is* wrong: every artifact I mutated was restored, and D1-D5 show only that a wrong value *would not be caught*. No efficacy, safety, selectivity or readiness statement, no wet lab, no patient data, no new source.
- **The ranking in R5 is my judgement** over a `PRIMARY` reference map. Reasonable owners could order ranks 3-5 differently.
- **Model identity is SELF-REPORT, not independently verified.** HEAD moved twice mid-run; I verified no file I measured changed rather than assuming it.

---

## Stop condition

Stated before measurement, five parts, quoted above. **MET in full**, with two parts qualified honestly: (1) is met for 52 of 130 modules with the remaining 78 explicitly labelled Class D/E and not asserted either way; (3) is exceeded — five demonstrations rather than three, all with real module exit codes — but the module that motivated the question (`emc_fourth_cohort_quant.py`) is deliberately **NOT RUN** because its `--check` writes, and that is recorded as `PROPOSED (NOT RUN)` rather than presented as a pass. Nothing was written into the Git tree; no fix was authored; no ceiling was raised; no guard was weakened.

---

## Tool-call and wall-clock count actually used

**23 tool calls** (all `Bash`), **6 minutes 8 seconds** wall clock (`03:13:33Z` → `03:19:41Z`), plus report drafting. Well inside the ~40-call / ~40-minute target; I returned on meeting the stop condition rather than padding.

---

## Next concrete action

**One successor, sized to fit and disjoint from every open repair in this campaign: resolve the 78 unclassified modules (Class D's 22 `return check()` delegations and Class E's 56) by reading each `check()` body, and publish the completed 130-module publish-vs-gate census.** It needs no network, no repair authorship, and no re-run of any closed endpoint — only source reading plus the same mutation harness for any new Class A/B module it finds. That converts my lower bound of 10 into a total, which is what the owner needs before deciding between Option 1 (0 test functions) and Option 2 (2 of the 3 remaining `commit-loop` slots), because Option 2's allowlist cannot be written until Class D and E are resolved.

**For the module owners, independent of that census and available now:** the ten Class A+B modules named in R2/R3 can each adopt the whole-document comparison idiom that 42 sibling modules already use, at **zero** test-function cost. Start at rank 1 (`aso_delivery_antigen.py:838-839`) and rank 2 (`emc_fourth_cohort_quant.py:938-941`) — those are the two whose values reach `systems/graph/`. Expect first honest runs to go red; that is the gate working, and the fix is the drift, never the guard.

**Not recommended:** placing any new test in `commit-loop` before Option 1 is done. With 1497/1500 measured on the real writer, the three remaining slots are worth more than a guard against a class that ten in-place edits would eliminate.
