<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:10:00Z UTC
     agent id a4209471951cc35a4 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a4209471951cc35a4.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

**W20g** · lane 20 refill · OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 03:02:19 UTC 2026` · `date -u` **end**: `Tue Sep  8 03:04:45 UTC 2026`

`git rev-parse HEAD` **start**: `fc6ed92999c26f52c47668d1c126321a5f51d1b5` · **end**: `4bd79b3bca255451dc5b25aaafa882e0ebed02e8`. **HEAD moved under me mid-run** (the coordinator committed five other workers' reports). I checked the exposure rather than assuming it away: `git diff --name-only fc6ed92..4bd79b3` lists exactly five files, all under `research/autonomy/opus-capacity-campaign-20260908/reports/`, and `git diff --stat fc6ed92..4bd79b3 -- research/modalities` is **empty**. No file I measured changed. Neither HEAD is the brief's frozen `92abbcb9`; I read the live checkout, and every number below is additionally anchored to content hashes, not to a commit.

`git status --porcelain` **start**: empty. **end**: empty. **I wrote nothing into the tree.** All execution under `/tmp/claude-0/w20g/`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (the four long proxy lines — `no_proxy`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are retained verbatim in the transcript, contain no model information, and are elided here as `...`):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=... (proxy list, no model information)
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
GLOBAL_AGENT_NO_PROXY=... (proxy list, no model information)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=... (truststore + proxy, no model information)
NO_PROXY=... (proxy list, no model information)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=... (proxy list, no model information)
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

**Stop when all four dispatch items are answered from committed data with no network: (1) every panel/assignment denominator in `emc-fourth-cohort-quant.json` enumerated with `file:line` and the exact set it counts; (2) each recomputed independently from the committed TSVs, agreement or disagreement reported with both numbers; (3) the `unassigned` label decomposed into offered-and-unmatched versus never-offered with both counts and a named downstream consumer; (4) the artifact's own `_method`/caveat fields checked verbatim for disclosure.** — **MET.** All four answered. Returning immediately.

---

## Question

**Are the denominators `research/modalities/emc-fourth-cohort-quant.json` publishes actually consistent with the committed TSVs, and what exactly does each one count?**

Open because W20f measured the intersection filter's *exclusion* (211,362 of 213,007) but audited no published count against the tables. W20f's finding implies a specific denominator hazard nobody had quantified: `n_probes_unassigned` is computed over the offered set at `:450`, while the string `unassigned` is written over the union set at `:586`. Whether those two populations are the same size, and whether anything downstream reads them as the same thing, was unmeasured. This needs no network: the matcher's output is already committed.

---

## Prior-work check

| Command | What it showed |
|---|---|
| `grep -n "n_probes_offered\|n_probes_unassigned\|n_probes_in_every_read_run\|n_runs_intersected\|n_probes_common_to_every_read_run\|n_genes_with_at_least_one_assigned_probe\|probe_counts_n_rows\|gene_counts_n_rows\|n_probes_matched\|unassigned" research/modalities/emc_fourth_cohort_quant.py` | 16 hit lines; every published counter located and read in context (`:394–460`, `:555–600`, `:755–840`, `:905–955`). |
| `grep -rn "emc-fourth-cohort-probe-counts\|assigned_gene\|n_probes_unassigned\|n_probes_offered\|n_genes_with_at_least_one_assigned_probe" --include=*.py --include=*.md --include=*.json --include=*.yml --include=*.tex .` | Four real downstream consumers outside the module: `expression_validation_readiness.py`, `emc_fourth_cohort_route_readout.py`, `systems/graph/routes.json`, `systems/views/L2-rt-immunocytokine.md`, plus the CI workflow that publishes both TSVs. |
| `grep -rn "213,007\|213007\|212,101\|212101\|211,362"` | `213007` appears in exactly three places, all provenance copies. **`212101` and `211362` appear nowhere in the tree** — the decomposition below is not published anywhere. |
| Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W20f-probe-intersection-filter.md` (§Question–§Result-6) | W20f's §6 repair is already returned; I did not re-author it. |

**Confirmed not replayed.** I did **not** re-run W20e's EWSR1 endpoint and computed no δ, p-value or panel percentile on any re-derived panel. I did **not** author a filter repair. No reagent designed. **No network request of any kind**: the Ensembl fetch (`_ensembl_fasta_url`, `:409`) and the vendor TempO-Seq manifest remain honest unrecovered sources and were not attempted, probed or routed around. No content-policy refusal was encountered. I also did **not** run `emc_fourth_cohort_quant.py --check`, because reading `:932–941` shows it calls `derive()` unconditionally, which calls `_write_probe_tsv` (`:817`) and writes `GENE_TSV` (`:829`) — it would have written into the repository, violating write isolation. Recorded as `PROPOSED (NOT RUN)`.

---

## Method / inputs

| Input | Path | sha256 (measured) | Use |
|---|---|---|---|
| The artifact under audit | `/home/user/Rare-cancers/research/modalities/emc-fourth-cohort-quant.json` | `1769b3f0ee01f1a640dabc6c4f36ce86630ff62f87249400e070a4638fcf5165` | the published denominators |
| Probe × run table | `.../emc-fourth-cohort-probe-counts.tsv` | `c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc` | independent recomputation, 213,007 rows × 12 run columns |
| Gene × run table | `.../emc-fourth-cohort-gene-counts.tsv` | `8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc` | independent recomputation, 862 rows × 12 |
| The generator | `.../emc_fourth_cohort_quant.py` | — | `file:line` for every counter |
| Consumers | `.../expression-validation-readiness.json`, `.../emc-fourth-cohort-route-readout.json`, `systems/graph/routes.json`, `systems/views/L2-rt-immunocytokine.md`, `.github/workflows/emc-expression-datasets.yml` | — | how each denominator is re-served |

**Tools:** Python 3.11 stdlib only (`json`, `hashlib`, `collections`). No third-party package, no network, no GPU, no paid API. Script at `/tmp/claude-0/w20g/recompute.py`.

**Operational definition, load-bearing and used throughout:** "present in run *r*" = a **non-zero** cell. This is the code's own definition — `_read_probe_tsv` (`:558–566`) inserts a key only `if n:`, so a zero cell is a *missing key*. Per the artifact's own `⛔ a_zero_in_the_probe_table`, a zero means "not among the counts PERSISTED for that run", **not** a measured zero. Every count below is a count of *persistence*, and treated as missing data, never as a measured absence.

---

## Result

### 1. Every published panel/assignment denominator, and the exact set it counts

All `file:line` in `research/modalities/emc_fourth_cohort_quant.py`. `PRIMARY` (code reading + recomputation).

| Published key (JSON path) | Emitted at | Computed at | **The set it actually counts** | Value |
|---|---|---|---|---|
| `probe_map.n_probes_offered` | `:447` | `:724` `probes = sorted(seqs)` | sequences persisting in **all 12** runs — the intersection, the only list ever shown to the matcher | 1,645 |
| `probe_map.n_probes_assigned_to_one_gene` | `:448` | `:443` `unique` | offered probes whose best-core hits resolve to **exactly one** gene symbol | 906 |
| `probe_map.n_probes_matching_several_genes` | `:449` | `:444` `multi` | offered probes hitting **≥ 2** symbols | 77 |
| `probe_map.n_probes_unassigned` | `:450` | `len(probes) − len(unique) − len(multi)` | **offered probes with no verbatim hit at any core length. Denominator = 1,645, never 213,007.** | 662 |
| `probe_map.per_core_length.{50,42,34}.n_probes_matched` | `:430` | `len({h["probe"] …})` | **distinct offered probes** with ≥ 1 hit at that core length (not hits, not transcripts) | 976 / 976 / 983 |
| `probe_map.per_core_length.*.fraction_of_probes_matched` | `:431–432` | `/ len(probes)` | same numerator **over the offered 1,645** | 0.593313 / 0.593313 / 0.597568 |
| `probe_map.n_probes_in_every_read_run` | `:727` | `len(probes)` | identical set to `n_probes_offered` — the same 1,645 published twice under two names | 1,645 |
| `probe_map.n_runs_intersected` | `:728` | `len(runs)` | cache entries carrying a `counts` dict | 12 |
| `n_probes_common_to_every_read_run` | `:802` (via `:775`) | copy of `n_probes_in_every_read_run` | the same 1,645 published a **third** time | 1,645 |
| `n_genes_with_at_least_one_assigned_probe` | `:803` | `len(gene_counts)` | distinct symbols in the `p2g` map that accumulated ≥ 1 read | 862 |
| `probe_counts_n_rows` | `:820` | `len(body.strip().split("\n")) − 1` | rows of the probe TSV = the **union** over all 12 runs | 213,007 |
| `gene_counts_n_rows` | `:833` | `len(gene_counts)` | same set as `n_genes_with_at_least_one_assigned_probe` | 862 |
| `per_run.*.n_sequences_persisted` | `:762` | from the phase-quant cache | per-run non-zero cells | 19,019 – 39,456 |
| `per_run.*.n_retained_sequences` | `:759` | LossyCounter retention | per-run sequences retained **before** persistence trimming — a *different, larger* set | 22,414 – 43,138 |

**Two denominators, three names.** `n_probes_offered`, `n_probes_in_every_read_run` and `n_probes_common_to_every_read_run` are the same 1,645 sequences published under three keys in two places. That is redundant but not wrong, and `n_runs_intersected: 12` sitting beside them is exactly the field that lets a reader see the intersection for what it is.

### 2. Independent recomputation from the committed TSVs — every published count agrees

`PRIMARY`. RUN, exit 0. Recomputed from the TSV bytes with no reference to the JSON except for comparison.

| Quantity | Published | **Recomputed** | Verdict |
|---|---|---|---|
| `probe_counts_sha256` | `c689e0fd…d26fc` | `c689e0fd…d26fc` | **agree** |
| `gene_counts_sha256` | `8aa3064a…180cc` | `8aa3064a…180cc` | **agree** |
| `probe_counts_n_rows` | 213,007 | 213,007 | **agree** |
| `n_probes_common_to_every_read_run` / `n_probes_offered` / `n_probes_in_every_read_run` | 1,645 | 1,645 (rows with all 12 cells non-zero) | **agree** |
| `n_runs_intersected` | 12 | 12 (run columns in the TSV header) | **agree** |
| `n_probes_assigned_to_one_gene` | 906 | 906 (rows whose `assigned_gene` ≠ `unassigned`) | **agree** |
| `n_genes_with_at_least_one_assigned_probe` | 862 | 862 (distinct symbols in the probe TSV) | **agree** |
| `gene_counts_n_rows` | 862 | 862 (rows of the gene TSV) | **agree** |
| gene symbol **sets** (probe TSV vs gene TSV) | — | identical | **agree** |
| gene TSV cells vs per-gene sums over the probe TSV | — | **0 of 10,344 cells disagree** | **agree** |
| `per_run.*.n_sequences_persisted` (12 values) | 39,456 … 35,436 | identical, **0 of 12 mismatches** | **agree** |
| `probe_gate.checks[1].measured` = 9,594 | 9,594 | equals `per_run.SRR35940646.n_sequences_covering_80pct` | **agree** |
| identity `offered = unique + multi + unassigned` | 1,645 | 906 + 77 + 662 = 1,645 | **agree** |
| `per_core_length.34.n_probes_matched` = 983 | 983 | = 906 + 77; 983/1645 = 0.597568 as published | **agree** |

**No disagreement was found. Every count and denominator this artifact publishes about the probe panel or the gene assignment reproduces exactly from the committed tables, and the two TSVs are internally consistent with each other to the cell.** That is a real result and it is worth stating plainly: the arithmetic is sound. The defect below is not an arithmetic error.

One structural observation, `PRIMARY`: **all 906 gene-labelled rows sit at k = 12 and none sits anywhere else** (recomputed k-distribution of labelled rows: `{12: 906}`). The label covers the intersection and nothing outside it — independent confirmation of W20f's mechanism from the label column rather than from the code.

### 3. **THE LOAD-BEARING FINDING — one string, three disjoint populations**

`PRIMARY`. RUN, exit 0. The probe TSV carries **212,101** rows labelled `unassigned`. `n_probes_unassigned` is **662**. These are not the same quantity, and the 322-fold gap is not published anywhere.

| Population inside the single string `unassigned` | Count | % of the label | % of the 213,007-row table | What is actually true of it |
|---|---|---|---|---|
| **Offered and unmatched** | **662** | **0.3121 %** | 0.3108 % | Shown to the matcher; no verbatim hit at any of the three core lengths. **The only population `⚠ unassigned_means` describes.** |
| **Offered and multi-gene** | **77** | 0.0363 % | 0.0361 % | Shown to the matcher and **matched** — to ≥ 2 symbols. `probe_to_gene` holds only `unique` (`:456`), so `:586` `(gene_of or {}).get(pr)` misses them and they are written `unassigned` **despite having matched**. |
| **Never offered** | **211,362** | **99.6516 %** | 99.2277 % | Excluded by the intersection at `:723` before the matcher ran. **Never tested at any core length.** Includes W20f's candidate EWSR1 (k = 10), TCF12 (k = 11, k = 10), TFG (k = 11) and **NR4A3 (k = 9)** sequences. |
| **Total** | **212,101** | 100 % | 99.5747 % | |

**The dispatch asked for the fraction: 0.31 % of the `unassigned` label is "offered and unmatched"; 99.65 % is "never offered".** Only **1,645 of 213,007 rows — 0.77 % of the table — were ever eligible for a gene label at all**, and 906 (0.43 %) got one.

I found a **third** population the dispatch did not anticipate, and it is the sharper defect of the two: the 77 multi-gene probes are the one group where `unassigned` is affirmatively **contradicted** by the artifact's own data. `probe_map.n_probes_matching_several_genes: 77` and the full `probe_to_several_genes` map are computed at `:444`, then dropped from the published JSON at `:801` (`if k not in ("probe_to_gene", "probe_to_several_genes")`) and never reach the TSV. A sequence that matched two genes and a sequence never shown to the matcher receive the identical string.

**Would a downstream consumer read the combined label as the first sense? Two answers, and they differ.**

- **`research/modalities/emc-fourth-cohort-route-readout.json` — YES, at one point, and it is the live one.** Its `⛔ _what_a_false_row_is_not` reads: *"It means no probe in this deposit was matched to that gene by this quantifier — emc-fourth-cohort-quant.json → probe_map.'⚠ unassigned_means' and '⛔ gene_counts_units'. The gene may be on the panel and unmatched, or off it."* The disjunction offered to the reader is **{on the panel and unmatched} ∪ {off the panel}**. It has no third branch for *on the panel, in this deposit, sequenced in nine of twelve runs, and never shown to the matcher* — which is where W20f placed the NR4A3 candidate. This artifact serves `AUT-PD-116` and its verdicts are transcribed into `systems/graph/routes.json` and `systems/views/L2-rt-immunocytokine.md`, where the published conclusion is *"TNC has no assigned probe at all"* → *"the tenascin parent gene is not readable in this cohort at all"* → *"the answer is NO"*. **`UNKNOWN`, not a refutation:** I did not and cannot determine offline whether a TNC sequence sits in the 211,362 — that needs the matcher and therefore the denied Ensembl fetch. What I can say is that the "NO" rests on a two-branch disjunction that is missing a branch covering 99.65 % of the label.
- **`systems/graph/routes.json` and the L2 view — NO, and they deserve credit for it.** The FN1 sentence is scoped exactly right: *"FN1 has exactly one assigned probe **across the 1,645 probes common to every run**"*. That phrasing names the real denominator inline. `expression_validation_readiness.py:253` likewise carries `offered_probes` (1,645) in the same `existing_values` dict as `unassigned_probes` (662), so the correct denominator travels with the number. It also asserts the identity at `:228` (`n_probes_offered == unique + multi + unassigned`) — a genuine internal check.

The exposure is worst for a reader of the **TSV alone**. Its header is `probe_sequence<TAB>assigned_gene<TAB>…` with **no legend, no caveat and no row count of the offered set**, and it is committed *and* uploaded as a standalone CI artifact (`.github/workflows/emc-expression-datasets.yml:1078, :1420`). A consumer computing "the unassigned fraction of this panel" from the file as shipped gets **212,101 / 213,007 = 99.57 %**; the same phrase computed from the JSON gives **662 / 1,645 = 40.24 %**. Both are derivable from committed data; neither is labelled; they answer different questions and nothing in the shipped files says so.

A smaller related gap, `PRIMARY`: the `--check` drift keys at `:940–941` are `probe_gate`, `n_runs_read`, `n_probes_common_to_every_read_run`, `n_genes_with_at_least_one_assigned_probe`, `gene_counts_sha256`. **`probe_counts_sha256` is published but is not drift-gated**, so the 213,007-row table could change without `--check` reporting drift, while the 862-row table could not.

### 4. Does the artifact disclose this? Partly — and where it is honest it is very honest

Verbatim, from `emc-fourth-cohort-quant.json` and its generator.

**What is disclosed, and is correct — credit where it is due.**

> `⛔ a_zero_in_the_probe_table`: *"means the sequence was not among the counts PERSISTED for that run — it may have been observed below the persistence cap. It is not a measurement of zero reads."*

That is exactly right, it is the rule this campaign asked me to apply, and the file states it before anyone else had to. Likewise:

> `⛔ gene_counts_units`: *"… A gene with no assigned probe is ABSENT FROM THIS TABLE, which is a statement about the panel and the matcher, never about the tumour."*

and the module docstring (`:38–41`):

> *"⛔ EVERY READING IS SEPARATE FROM WHETHER IT COULD BE TAKEN. A probe with no transcript match is `unassigned`, never 'not expressed'; … An absent reading is not a reading of absence (CLAUDE.md §4)."*

The filter is also **not hidden**: the code comment at `:718–719` states *"a probe is a sequence retained in EVERY run that was read — the intersection is the conservative set, and its size is reported beside the per-run counts"*, and the size **is** reported, three times, with `n_runs_intersected: 12` beside it. `_what_this_is_not` correctly refuses panel confirmation and the patient-count reading. **The ingredients for the whole decomposition in §3 are published.** A reader who divides 1,645 by 213,007 can see the gap.

**What is not disclosed.** The only field that defines the word is:

> `⚠ unassigned_means`: *"no verbatim match to a human cDNA or ncRNA transcript at any core length tried. That is a statement about this matcher, NOT about the probe: a probe spanning a junction the sequence set does not contain, or carrying non-target bases, is unassigned here and is still a real probe."*

This is a true and careful statement **about 662 of the 212,101 rows that carry the label (0.31 %)**. Applied to the 211,362 never-offered rows it is **false as applied** — nothing was "tried" on them at any core length. Applied to the 77 multi-gene rows it is false outright — they matched. And the field lives in `probe_map`, i.e. beside the offered set, while the label it defines is written over the union set at `:586`. No `_method` or caveat field anywhere in the artifact, the inputs cache, the route readout or the readiness file states that the TSV's `unassigned` spans more than one population, and the strings `212101` and `211362` occur nowhere in the tree.

**Verdict on item 4: partially disclosed. The persistence caveat and the intersection's size are disclosed, clearly and unprompted, and that is to the file's credit. The composition of the `unassigned` label is not disclosed anywhere, and the one field that defines the word describes 0.31 % of the rows that carry it.**

---

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24 x86_64, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, `Python 3.11` stdlib only, no network, cwd `/tmp/claude-0/w20g`.

```
$ python3 /tmp/claude-0/w20g/recompute.py ; echo "EXIT=$?"
probe sha256 c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc json c689e0fd…
gene  sha256 8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc json 8aa3064a…
n_probe_rows 213007 json 213007 n_run_cols 12
rows labelled with a gene: 906  json n_probes_assigned_to_one_gene 906
rows labelled "unassigned": 212101
distinct genes in probe TSV: 862 json n_genes_with_at_least_one_assigned_probe 862
k=12 (all runs nonzero): 1645 json n_probes_common_to_every_read_run 1645 json n_probes_offered 1645
k distribution of labelled rows: {12: 906}
offered-and-unmatched (json 662): 662  multi: 77
check offered = uniq+multi+unassigned: 1645 == 1645
never offered = 211362  (label total 212101 = 662 unmatched + 77 multi + 211362 )
gene rows 862 json gene_counts_n_rows 862 cols 12
gene-TSV cells disagreeing with probe-TSV per-gene sums: 0
gene sets identical: True
per-run mismatches: 0
full k histogram: {1: 162981, 2: 17404, 3: 8246, 4: 4103, 5: 4051, 6: 2668, 7: 2644,
                  8: 2561, 9: 2493, 10: 2217, 11: 1994, 12: 1645}
EXIT=0
```

The k histogram reproduces W20f's table exactly, from an independently written script — an incidental replication of that report's central measurement.

```
$ sha256sum research/modalities/emc-fourth-cohort-quant.json
1769b3f0ee01f1a640dabc6c4f36ce86630ff62f87249400e070a4638fcf5165
```
This matches the `file_sha256` that `expression-validation-readiness.json:12626` pins for every one of its `quant#/…` pointers, so the readiness file's provenance chain to this artifact is **intact and verified**, not merely asserted.

```
$ git diff --stat fc6ed929… 4bd79b3b… -- research/modalities
(empty — exit 0)
$ git status --porcelain          # start and end
(empty)
```

**PROPOSED (NOT RUN):** `python research/modalities/emc_fourth_cohort_quant.py --check`. Not run **by design** — `:928` calls `derive()` before the drift comparison, and `derive()` writes `PROBE_TSV` (`:817`) and `GENE_TSV` (`:829`). Running it would have written into the Git tree. Its outcome is **UNKNOWN**; no drift claim is made here from it.

---

## Limitations

- **Nothing here is a clinical claim.** Runs are not samples and samples are not people. This is an audit of counts in a file.
- **Every count is a count of persistence, not of biology.** A zero cell means "not among the counts persisted for that run", per the artifact's own words. Treated as missing throughout; no zero was read as a measured zero anywhere in this report.
- **I did not run the matcher and therefore cannot say how many genes a repaired filter recovers.** That still needs the denied Ensembl fetch and remains **UNKNOWN**, exactly as W20f left it. Nothing here estimates it.
- **The 211,362 never-offered sequences are not established to be probes.** The TSV column is named `probe_sequence` and the file `probe-counts`, but only the 1,645 were ever tested. Their identity is **UNKNOWN**; some are certainly sequencing error (W20f measured ~1.3 % as 1-nt frame shifts of persisted sequences, leaving ~98.7 % unresolved offline).
- **The TNC/FN1 route conclusion is flagged, not refuted.** I show its stated disjunction is missing a branch. Whether TNC has a sequence among the 211,362 is **UNKNOWN** offline. This report does not reopen, re-grade or unblock `AUT-PD-116`, `RT-IMMUNOCYTOKINE` or any route, and does not touch `systems/graph/`.
- **Agreement is not correctness of design.** Every published number reproduces; the finding is that one *label* conflates three populations, not that any arithmetic is wrong.
- Model identity is **SELF-REPORT, not independently verified**. HEAD moved mid-run; I verified no audited file changed rather than assuming it.

---

## Tool-call and wall-clock count actually used

**15 tool calls** (all `Bash`; one produced a persisted large-output file I did not need to re-read). **Wall clock ≈ 2.5 minutes** measured (`03:02:19Z` → `03:04:45Z`), plus report drafting. Well inside the ~40-call / ~40-minute target; I returned on meeting the stop condition rather than padding.

---

## Next concrete action

**One successor, and it needs no network, no repair authorship and no re-run of any closed endpoint:** the smallest honest fix to the defect in §3 is a **label change and one field**, not a filter change — so it is disjoint from W20f's repair and can land whether or not that repair is ever accepted. Concretely, for a future owner of `emc_fourth_cohort_quant.py`: at `:586`, replace the single `unassigned` string with the three states the code already knows — `unassigned` (offered, no hit), `multi_gene` (offered, ≥ 2 hits; the symbols are already in `probe_to_several_genes` at `:444`), and `not_offered` (excluded by the intersection at `:723`) — and add one artifact field stating the 662 / 77 / 211,362 split with the offered denominator named. That converts a defect into a disclosure without moving a single committed count: the 906 labelled rows, the 862 genes, both TSV hashes and every gene count are untouched by it. **I did not write it**; authorship is the successor's, and it is a code change requiring an owner and the normal commit gate.

A second, smaller item for whoever holds the module: `probe_counts_sha256` is published but absent from the `--check` drift keys at `:940–941`, while `gene_counts_sha256` is present. Adding it is a one-line change with no scientific content.

**Not recommended:** re-deriving the panel to re-test any endpoint on it. W20d refused that iteration and W20e's endpoint is closed at NULL; nothing in this audit disturbs either.
