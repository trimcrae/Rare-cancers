<!-- collected 2026-09-08T05:01:26Z by campaign coordinator; agent id a0a16d7157def671c; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a0a16d7157def671c.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

W73, gate-artifact-provenance lane. Model identity: **SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — I am told I am Claude Opus 5 (`claude-opus-5`); no environment variable names a served model, so this is not observed fact.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (literal, start of run; no `*MODEL*` variable exists):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,...
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy config)
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

**Start:** `Tue Sep 8 04:53:48 UTC 2026`, HEAD `fcb36d3c651223d90b98c0cb64169bb106e6e060`, `git status --porcelain` **empty**.
**End:** `Tue Sep 8 04:58:16 UTC 2026`, HEAD `d5034489077eee6a11ccee088bd5bfccf6f7a8e1`, `git status --porcelain` **empty**. HEAD advanced mid-run (coordinator collection, expected per COMMON-BRIEF §1). Scratch `/tmp/claude-0/w73/` deleted; `ls` confirms `No such file or directory`. I wrote nothing into the repository and ran no git write operation.

## Question

For every JSON/CSV/Markdown artifact read by a `--check` gate in `scripts/preflight.sh`, does it have a **producer** (a module that writes it, so `--check` can compare recomputed against committed) or is it **HAND-MAINTAINED** (no writer anywhere, so `--check` can only validate shape)? And: how many gate-read artifacts are hand-maintained, and which are small enough that ordinary editing could empty them?

Open because W44 established the property for one row by execution but never censused it: the "row 17 is the exposed row" result rested on a single artifact's writer-absence, with no denominator.

## Prior-work check

Read in full: `COMMON-BRIEF.md` (510 lines), `CORPUS-CONTEXT.md` (82), `CLOSED-WORK.md` (70). Taken as given, not redone: W44's 4-of-18 vacuous-pass census (rows 11, 16, 17, 18) and its per-row mechanism split; W45's 26-module regenerate-then-check escape census; W37c's finding that `research/manuscripts/emc-systems-map.json` **has no generator today** — which my independent writer-grep reproduces; W47/W51/W55 on `pinned-figures.json`, `lint_consistency.py` and the citation ledger. I did not run `scripts/preflight.sh`, did not run `atr_hrd_sarcoma_series.py` in any mode, ran no `--refresh`, and executed no gate at all — this run is pure source analysis plus committed-file parsing. W25 not read or referenced.

The 18 rows are `scripts/preflight.sh:847-864`; the ordering there confirms W44's numbering (17 = `scripts/citation_debt.py`, 18 = `scripts/news_match.py`, 16 = `scripts/trigger_scan.py`, 11 = `aso_deposit_drift.py`).

## Method and inputs

Read-only, entirely under `/tmp/claude-0/w73/` (now deleted), against the live checkout at the HEADs above.

1. **Artifact extraction.** Regex over each of the 18 modules' source for quoted `*.json|*.csv|*.md|*.tsv|*.fasta` literals; basenames resolved against `git ls-files`. **133 tracked artifacts** resolved; 5 unresolved fragments (`-graded.json`, `-research-article.md`, `-cover-letter.md`, `/_index.json`, `.build-stamp.json`) are f-string suffixes, not paths.
2. **Writer detection, three passes** (each pass added producers the previous missed — this is the main methodological finding):
   - *Pass 1*, literal write idioms (`open(...,"w")`, `write_text`, `json.dump`, `os.replace`, `to_csv`) referencing the basename or a variable assigned on a line containing it → 79 with a writer, 54 without.
   - *Pass 2*, broadened to helper-call verbs (`_write_json`, `dump`, `emit`, `save`, `export`) → recovered 10 more; 44 left.
   - *Pass 3*, **proximity** (any write idiom within ±25 lines of a non-test mention, tests excluded) → recovered the "`<artifact>` is stale; re-run without `--check`" idiom, where the producer names the file only in its own staleness message: `aso_parent_null.py:878`/`:874`, `aso_parent_gap_pairing.py:288`/`:284`, `junction_aso_thermo.py:446`/`:442`.
3. **Knob-parameterised producers.** Remaining "no-writer" variants were checked for env-knob construction. `aso_premrna_offtarget.py:73` (`PREMRNA_OUT`), `aso_genome_offtarget.py:112` (`GENOME_OUT`), `junction_aso_offtarget.py:47`, `junction_aso_thermo.py:93`, `aso_parent_gap_pairing.py:90,93` (all `OUT_SUFFIX`), with `.github/workflows/aso-offtarget.yml:330,715` setting them. Every `-noncoding-acceptor`, `-18mer-5-8-5`, `-20mer-5-10-5`, `-ewsr1intron2`, `-taf15intron2`, `-genomic`, `-bp200-8`, `-bp200-8-gapres` variant is therefore **produced**, not hand-maintained.
4. **Residual adjudication.** Each remaining candidate grepped individually across `*.py *.mjs *.sh *.yml` for any write context; every hit was a read-only `open(...)`, a docstring, or another module writing its *own* artifact while quoting this path as provenance.
5. **Record counts** parsed from the committed JSON / line-counted for Markdown.

## Result

### A. Hand-maintained artifacts read by a preflight `--check` gate — **26** of 133 (19.5%)

All rows `PRIMARY` (writer-absence is a property of committed bytes I measured, not a prediction). "Rows" are `preflight.sh:847-864` ordinals. Producer column is `HAND-MAINTAINED` = no writer found in `systems/`, `scripts/`, `research/`, `.github/` by any of the three passes.

| Artifact | Size (records) | Producer | Gate(s) that read it | What that gate can still catch if emptied |
|---|---|---|---|---|
| `research/literature/citation-debt.json` | **4 rows** | HAND-MAINTAINED (only read: `scripts/citation_debt.py:34,56`) | 17 | **Nothing** — measured vacuous by W44 |
| `research/method-watch-triggers.json` | **39 triggers** | HAND-MAINTAINED (`citation_debt.py:35`, `news_match.py:73`, `trigger_scan.py`) | 16, 17, 18 | Row 17: nothing (its only use is the `trigger ∈ registry` membership test at `:76`, vacuous over an empty ledger). Rows 16/18 retain their own produced-output compares |
| `research/manuscripts/emc-systems-map.json` | 22 keys; routes=40, instruments=32, revival_triggers=28 | HAND-MAINTAINED — independently reproduces W37c | 14, 16 | Row 14's registry of fixed paths; row 16's produced `IDEAS.md`/scan-report compare |
| `systems/graph/blockers.json` | list of **21** | HAND-MAINTAINED (`trigger_scan.py:474`, read-only) | 16 | Row 16's byte-compare of its own generated `IDEAS.md` |
| `research/literature/venue-fee-routes-2026-08-10.json` | 9 keys; verdicts=3, `_retrieval`=4 | HAND-MAINTAINED (`submission_packet.py:380`) | 8 | Row 8's `SUBMISSION-PACKET.md` recomputation |
| `research/literature/submission-reference-metadata-2026-08-09.json` | records=**25** | HAND-MAINTAINED | 3, 10 | Row 3's produced reference lists; row 10's archive digest |
| `research/literature/tcf12-nr4a3-breakpoint-primary-sources.json` | records=**4** | HAND-MAINTAINED | 10 | Row 10's `--check-archive` digest over the manifest |
| `research/manuscripts/aso/fusion-junction-aso-data-sources.json` | entries=**9** | HAND-MAINTAINED (`submission_citations.py:60`) | 3, 10 | Row 3's generated references file |
| `research/manuscripts/aso/fusion-junction-aso-2026-citation-resolution.json` | records=**3** | HAND-MAINTAINED | 10 | Row 10's digest |
| `research/manuscripts/aso/lit-targets-aso-gap-length.json` | records=**7** | HAND-MAINTAINED | 10 | Row 10's digest (note: `aso_gap_length_tradeoff.py:98` raises if a PMID is absent — a *different* module, not this gate) |
| `research/manuscripts/aso/lit-targets-aso-thermo.json` | 5 keys; records_returned=**3** | HAND-MAINTAINED | 10 | Row 10's digest |
| `research/manuscripts/aso/lit-targets-aso-round7-precedents.json` | 10 keys, no primary record array | HAND-MAINTAINED | 10 | Row 10's digest |
| `research/manuscripts/aso/lit-targets-nr4a-redundancy.json` | records=**4** | HAND-MAINTAINED (`submission_citations.py:209`) | 3 | Row 3's generated references |
| `research/manuscripts/aso/lit-targets-aso-bibliography-completion.json` | records=**24** | HAND-MAINTAINED (`submission_citations.py:218`) | 3 | Row 3's generated references |
| `research/manuscripts/fusion-partner/lit-targets-partner-events.json` | round1=38, round4=16, round2=14 | HAND-MAINTAINED (`submission_citations.py:205`) | 3, 10 | Row 3's generated references |
| `research/modalities/emc-test-article-routes.json` | routes=3, sources=8, unresolved=7 | HAND-MAINTAINED | 10 | Row 10's digest |
| `research/modalities/nr4a3-deposited-junctions.json` | junctions=**5**, provenance=7 | HAND-MAINTAINED | 10 | Row 10's digest |
| `research/modalities/emc-condensate-pilot-T161-r1.json` | 23 scalar keys, **no arrays** | HAND-MAINTAINED (`emc_condensate_report.py:27`) | 12 | Row 12's produced CALVADOS findings Markdown |
| `research/manuscripts/aso/fusion-junction-aso-journal-article.md` | 432 lines | HAND-MAINTAINED (manuscript) | 2, 4, 10 | Rows 2/4 recompute coverage + word counts from it → mismatch |
| `research/manuscripts/aso/fusion-junction-aso-supplementary-information.md` | 211 lines | HAND-MAINTAINED | 3, 5, 10 | Row 5's produced sequence CSV/FASTA compare |
| `research/manuscripts/aso/fusion-junction-aso-paper-redteam.md` | 221 lines | HAND-MAINTAINED | 10 | Row 10's digest |
| `research/manuscripts/aso/aso-citations-priorart-2026-08-08.md` | 460 lines | HAND-MAINTAINED | 10 | Row 10's digest |
| `research/manuscripts/aso/aso-delivery-antigen-2026-08-08.md` | 321 lines | HAND-MAINTAINED | 10 | Row 10's digest |
| `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md` | 695 lines | HAND-MAINTAINED | 4 | Row 4's pinned word/figure counts recomputed → mismatch |
| `research/manuscripts/repurposing/repurposing-hypotheses.md` | 648 lines | HAND-MAINTAINED | 4 | Row 4's pinned counts |
| `research/manuscripts/surface-targets/emc-surface-target-landscape.md` | 872 lines | HAND-MAINTAINED | 4 | Row 4's pinned counts (`submission_metrics.py:323,329,333`) |

**Correction I applied to my own intermediate result:** `research/modalities/atr-hrd-sarcoma-series-quant-inputs.json` (rows 13, 14) first classified HAND, then **reclassified PRODUCER** — `research/modalities/atr_hrd_sarcoma_series.py:1352-1353` writes it via an f-string path (`paths_for(SERIES)`, `:98-100,105`), so no basename literal exists to grep. Its producer is network-dependent (`fetch()` at `:187`). Same for `atr-hrd-sarcoma-series.json` (`:1357,1367,1453`) and `-inputs.json` (`:1364`). I did not run that module in any mode.

### B. Producer-side result (107 of 133)

Every other gate-read artifact has a writer. Representative verified producers: `aso_genome_offtarget.py:112`, `aso_taf15_intron2_designs.py:60`, `emc_condensate_calvados.py:64,762` (+ dispatch at `:1078,1085`), `aso_parent_null.py:874`, `aso_parent_gap_pairing.py:93`, `junction_aso_offtarget.py:47`, `junction_aso_thermo.py:93`, `depmap_target_expression.py:188`, `venue_policy_browser_fetch.py:23`, `pgr_offtarget_locus_expression.py:132`, `news_match.py:417`, `vaccine_path_tables.py:243` (writes generated blocks *into* the Markdown manuscript). The producer column for these 107 is **heuristic-derived and spot-verified, not exhaustively hand-read** — see Limitations.

### C. The decisive structural result — per-gate composition

This is the generalisation W44's single row was pointing at. Counting hand-maintained artifacts as a fraction of each row's total artifact set:

| Row | Module | hand / total |
|---|---|---|
| 1 | `submission_tables` | 0/13 |
| 2 | `claim_coverage` | 1/9 |
| 3 | `submission_citations` | 6/13 |
| 4 | `submission_metrics` | 4/8 |
| 5 | `aso_sequence_manifest` | 1/22 |
| 6 | `aso_journal_tables` | 0/3 |
| 7 | `aso_offtarget_duplex_energy` | 0/1 |
| 8 | `submission_packet` | 1/5 |
| 9 | `vaccine_path_tables` | 0/5 |
| 10 | `aso_archive_manifest` | 15/83 |
| 11 | `aso_deposit_drift` | 0/3 |
| 12 | `emc_condensate_report` | 1/7 |
| 13 | `atr_hrd_sarcoma_series` | 0/3 (f-string derived) |
| 14 | `single_slot_identity` | 1/5 |
| 15 | `instrument_census` | 0/3 |
| 16 | `trigger_scan` | 3/9 |
| **17** | **`citation_debt`** | **2/2 — ALL HAND** |
| 18 | `news_match` | 1/3 |

**Row 17 is the only gate whose entire input set is hand-maintained**, and it is the only gate that produces no artifact of its own — `citation_debt.py` has no output path, so its `--check` has nothing to byte-compare. That, not the record count, is the property. Every other row owns at least one produced artifact, so emptying any hand-maintained *input* changes a recomputation and the byte-compare fails. This is an exact structural match to W44's measured 4-of-18, and it explains why: hand-maintained inputs are common (26 of 133), but they are almost always paired with a produced output that notices.

### D. Which hand-maintained artifacts are small enough to be emptied by ordinary editing

Taking "ordinary editing could empty it" as *one array, single-digit-to-low-tens records, plausibly cleared in one edit*: **13 of the 26** qualify — `citation-debt.json` (4), `tcf12-nr4a3-breakpoint-primary-sources.json` (4), `lit-targets-nr4a-redundancy.json` (4), `fusion-junction-aso-2026-citation-resolution.json` (3), `lit-targets-aso-thermo.json` (3), `nr4a3-deposited-junctions.json` (5), `lit-targets-aso-gap-length.json` (7), `fusion-junction-aso-data-sources.json` (9), `emc-test-article-routes.json` (3 routes), `systems/graph/blockers.json` (21), `lit-targets-aso-bibliography-completion.json` (24), `submission-reference-metadata-2026-08-09.json` (25), `method-watch-triggers.json` (39). The three 500-900-line manuscripts and `emc-systems-map.json` (100 records across three collections) are not credibly emptied by ordinary editing.

**But only two of those 13 sit behind a gate that could then pass vacuously** — `citation-debt.json` and `method-watch-triggers.json`, both at row 17. The other eleven feed rows that own a produced artifact. So the answer to "how many are exposed" is unchanged from W44 at **one row**, and my census establishes the denominator that makes that a finding rather than an anecdote.

### E. One incidental source-read finding, adjacent and distinct

`scripts/news_match.py:279-280`: if the queue file does **not exist**, `--check` prints `"news_match --check: no queue committed yet — nothing to validate"` and returns before any validation. That is a vacuous pass reachable by *deletion* rather than emptying — a different operation from the one W44's sweep tested, on a row W44 already classifies as vacuous. **SOURCE-READ ONLY, NOT EXECUTED.** I am not proposing a repair.

## Validation evidence

**RUN** (all read-only; `python3` = `/usr/local/bin/python3`; cwd `/home/user/Rare-cancers`; scratch under `/tmp/claude-0/w73/`, since deleted):

- `date -u; git rev-parse HEAD; git status --porcelain` — start `04:53:48Z` / `fcb36d3c…` / empty; end `04:58:16Z` / `d5034489…` / empty. Both exit 0.
- `grep -n "run_check\|^CHECKS\|--check" scripts/preflight.sh | head -80` → exit 0; the 18-row loop at `:847-864` verbatim.
- `python3 /tmp/claude-0/w73/census.py` → `resolved artifacts: 133 unresolved: 5`, exit 0.
- `python3 /tmp/claude-0/w73/writers.py` → `artifacts: 133 with candidate writer: 79 NO writer: 54`, exit 0.
- `python3 /tmp/claude-0/w73/writers2.py` → `re-checked 54 | still NO writer: 44`, exit 0.
- `python3 /tmp/claude-0/w73/prox.py` → recovered the staleness-message producers; exit 0.
- `grep -n 'environ.get("[A-Z_]*OUT…' research/modalities/{aso_premrna_offtarget,nr4a3_fusion_junction_atlas,junction_aso_offtarget,junction_aso_thermo,aso_parent_gap_pairing,aso_genome_offtarget}.py` and `grep -rn "PREMRNA_OUT|ATLAS_OUT|GENOME_OUT|…" --include=*.yml --include=*.sh --include=*.md .` → exit 0; knob defaults + `.github/workflows/aso-offtarget.yml:330,715,758`.
- Per-artifact residual grep over `*.py *.mjs *.sh *.yml` for the 12 uncertain paths → **zero write contexts**; the only hits were read-only `open(...)` at `test_trigger_board_filter.py:133`, `test_systems_check.py:502,536`, `trigger_scan.py:474`. Exit 0.
- `grep -n "QUANT_INPUTS|open(.*\"w\"|json.dump" research/modalities/atr_hrd_sarcoma_series.py` → `:1352-1353` writer; exit 0. **The module was never invoked**, in any mode.
- `grep -n "QUEUE|--check|--refresh" scripts/news_match.py` → `:279-280`, `:417`; exit 0.
- `rm -rf /tmp/claude-0/w73 && ls -d /tmp/claude-0/w73` → `No such file or directory`.

**PROPOSED (NOT RUN):** every emptying experiment. I ran no gate, made no `cp -a` sandbox copy, and mutated nothing. Column 5 of the table above ("what the gate can still catch") is **INFERRED** from the byte-compare mechanism W44 measured, except the `citation-debt.json` row, which is W44's measured result quoted.

## Limitations

- **The 107-artifact producer column is heuristic.** Detection is regex + proximity over `git ls-files`-tracked `*.py *.mjs *.js *.sh *.yml`. My own three passes plus the `atr-hrd-sarcoma-series-quant-inputs.json` correction show the false-negative mode is real (f-string and env-knob paths carry no greppable basename), so **the true hand-maintained count is an upper bound: ≤26, possibly fewer.** Producer *presence* claims I spot-verified by reading the line; producer *absence* claims for the 26 rest on the failure of three independent detectors plus a per-path manual grep — strong, but not a proof.
- Only tracked files were searched. An untracked or generated-elsewhere writer would be missed; `inputs/` is gitignored (W41) and excluded by construction.
- Path extraction is literal-string only. Row 13's three artifacts are f-string-derived and were recovered by hand; a similar construction elsewhere could hide an artifact from the 133 entirely. The 133 is a floor, not a complete gate-read surface.
- Five unresolved fragments were not chased.
- Gates outside the 18-row loop (`systems_check.py:609`, `emc_systems_map_check.py:627`, `receipt_schema.py:929`, `contract_check.py:1484`, `tier_budget.py:1507`, `derived_ids.py:1536`) are **not censused here** — out of scope for the bounded question.
- **This says nothing scientific.** Hand-maintained is not wrong; a producerless artifact is not unreliable. No artifact's content was graded, and nothing here bears on EMC efficacy, safety, selectivity or clinical readiness. No claim is made that any of these files is stale, mislabelled or incorrect.
- No content-policy refusal occurred in this run.

## Stop condition

Set up front: *return once every gate-read artifact path is classified producer-vs-hand-maintained with a `file:line` or a documented absence of writer, and the per-gate hand-fraction is computed.* **MET** at 133 artifacts / 18 rows / 26 hand-maintained, with the per-gate table complete. Returning without padding.

## Tool-call and wall-clock count actually used

**19 tool calls; 4 min 28 s wall clock** (04:53:48Z → 04:58:16Z). Both well under the ~40/~40 target.

## Next concrete action

For a human owner, not a worker: decide whether `citation_debt.py` should be a gate at all. It is the only preflight row with no produced artifact, and my census shows that is *why* it is escapable — not its 4 records. The two available shapes are (a) give the ledger a producer so `--check` becomes a recomputation compare, or (b) drop it from the 18-row loop and let it be a report. **I am not proposing, drafting or applying either**; the repository's own §6 rule against changing a guard to hide an error means this needs an owner ruling, and W44's measured vacuous pass is the evidence that ruling should rest on. The natural read-only successor in this lane is to extend the same census to the six non-loop `--check` gates at `preflight.sh:609,627,929,1484,1507,1536`, which no worker has covered.
