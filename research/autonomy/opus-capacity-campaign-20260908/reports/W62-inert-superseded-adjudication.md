<!-- collected 2026-09-08T04:57:32Z by campaign coordinator; agent id a17ba484a2e87e373; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a17ba484a2e87e373.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W62**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: `superseded[]` guard liveness — deciding whether the 23 inert entries are correctly or silently inert.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). No environment variable names a served model. Literal output of the prescribed command at start (pasted in full below; the end-of-run re-run returned the same set, abridged to the five non-proxy lines at the end of this report):

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
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy/truststore flags)
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

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 04:48:04 UTC 2026` | `Tue Sep  8 04:54:27 UTC 2026` |
| `git rev-parse HEAD` | `8a667406e875ae99c7d50347b2e895a177fcb048` | `fcb36d3c651223d90b98c0cb64169bb106e6e060` |
| `git status --porcelain` | 0 lines | 0 lines |

HEAD advanced under me (coordinator collection). Write isolation honoured: no repository write, no git write operation, no repair/patch/gate/test authored or proposed, no pattern widened, no alarm added, `scripts/preflight.sh` not run, `atr_hrd_sarcoma_series.py` not invoked. All execution under `/tmp/claude-0/w62/`, **deleted** (`ls` → `No such file or directory`). W25 not read or referenced.

## Question

For each of the 23 `superseded[]` entries in `research/manuscripts/pinned-figures.json` whose pattern matches nothing in any of the 29 `targets[]`: is it **CORRECTLY-INERT** (the retired value is genuinely gone from the tree) or **SILENTLY-INERT** (the value, or an equivalent phrasing, still exists somewhere the compiled pattern cannot reach)? Open because W47 measured the 23 and explicitly left this undetermined, and W28d named it as the nearest genuinely open question in the lane.

## Prior-work check

Read in full: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W47-pinned-figures-consumers.md`, `reports/W28d-transplant-test-40-would-match.md`. I take their numbers as given and re-derived only the identity of the 23 (to have the objects in hand): my independent recomputation returns **23 inert of 81**, and the id list matches W47's 23 **exactly, entry for entry**. I did not re-run the transplant set, the frame screen, the campaign resolution rate, the `literature-cache` question, or the `systems_check` baseline. `CLOSED-WORK.md` closes nothing in this lane. Campaign reports were excluded from every search (`research/autonomy/opus-capacity-campaign-20260908` filtered from the file walk and from every `grep`), per the instruction that they are not repository evidence and quote retired values freely. Live checkout only; I did not read the frozen corpus.

## Method and inputs

1. Loaded `research/manuscripts/pinned-figures.json`, compiled each `superseded[].pattern` with the same `re` + per-line semantics `check_superseded` uses (`lint_consistency.py:595-615`, matching on `_read_lines` output), scanned the 29 `targets[]` → the 23 inert entries.
2. Dumped every field of each of the 23 (`pattern`, `current`, `retired_by`, `note`, `artifact`, `must_not_appear_in`, `id_note`).
3. **Whole-repository scan**: walked all 7,604 files under `/home/user/Rare-cancers` (skipping `.git`, `node_modules`, `__pycache__`, binaries, and the campaign directory) and ran each of the 23 compiled patterns line-by-line over every text file, recording file:line and whether the file is a target.
4. For the six entries with zero repo-wide pattern hits, and for every entry whose retired value could be reworded, ran **value-level** greps for the retired quantities in alternative spellings (`126.17`, `77.28`, `79.59`, `99.59`, `1.528`, `1.574`, `0.005214`, `0.005369`, `87.8`, `cross-margin`, `reverses the order`, `8.78|22.28` near plan/ceiling, and the vaccine coverage constructions), then **read the surrounding prose** at every candidate site to decide what the occurrence asserts.
5. Confirmatory per-row re-match with the real compiled pattern for the four rows I grade SILENTLY-INERT, including a joined-adjacent-lines control to isolate line-wrapping as the mechanism.

**Grading rule, declared before scoring and applied uniformly.** A repo-wide textual occurrence is not by itself silent inertness — the registry retires *claims*, and it explicitly sanctions retained history (`commit_loop_gate13_446s_85_to_94_percent.current`: the old readings "were correct when taken"). So:

- **CORRECTLY-INERT** — no occurrence anywhere asserts the retired value as a current fact. Every occurrence is one of: the registry file quoting its own pattern; a dated correction/audit/review-round/ledger record; an explicitly marked "⚠ Superseded, retained" retention; or a raw provenance datum where the numeral denotes a different quantity (a per-host bench reading behind a median, a PDB coordinate, a PLUMED hill height).
- **SILENTLY-INERT** — at least one occurrence states the retired value, or an equivalent rewording of the retired construction, **as current**, in a place the compiled pattern cannot reach (outside `targets[]`, or inside a target but defeated by wording or line wrapping). Quoted with file:line.
- **UNDECIDABLE** — cannot be settled from committed text.

## Result

### Counts: CORRECTLY-INERT 19 · SILENTLY-INERT 4 · UNDECIDABLE 0

All rows `PRIMARY` (direct reading of committed source plus scans I ran). n = 23 of 23; no row unresolved.

| # | id | repo-wide pattern hits (targets/non-targets) | Grade | Decisive evidence |
|---|---|---|---|---|
| 1 | `aso_thermo_cross_margin_discordance` | 0 / 0 | **SILENTLY-INERT** | The sentence the pattern is written for is **in a target file**, `research/manuscripts/aso/fusion-junction-aso-research-article.md:1166-1167`: *"…because composition reverses"* / *"the order in 19.9% of cross-margin design pairs…"*. `check_superseded` matches per line; the pattern's `reverses the\s+order` straddles the wrap. Measured control: per-line match `False`, joined-with-previous-line match `True`. Pure wording/wrap drift, in scope. |
| 2 | `vaccine_coverage_wilson_intervals` | 0 / 7 | **SILENTLY-INERT** | The intervals the registry says are **"withdrawn"** (their pooling model refuted by its own input) are printed as current in `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md:58` (*"8.51%, 95% CI 8.26–8.76%"*), `:59` (*"27.4%, 95% CI 26.6–28.1%"*), `:246`, `:248`; also `research/manuscripts/modality-census/novel-modalities.md:302` and `…/novel-modalities-factcheck.md:132`. The pattern **matches those lines** — the gate simply cannot see the files, because `must_not_appear_in`/`targets` name only `emc-vaccine-development-path.md`. |
| 3 | `vaccine_e7_coverage_stated_without_a_panel` | 0 / 0 | **SILENTLY-INERT** | Retired construction = coverage stated without naming a panel. Present in **equivalent phrasing** at `fusion-junction-neoantigen-paper.md:246`: *"is now presented on **B\\*15:01 alone** — both of its strong binders are B\\*15:01 — and covers **≈8.5% of patients**"*, and `novel-modalities.md:301`: *"(presented on **B\\*15:01 alone**) covers **≈8.5%**"*. The pattern requires the literal `predicted to be presented on HLA-B*15:01 alone` or a table cell `| B*15:01 alone |`; neither form survives. Measured: pattern does **not** match line 246 even when joined with its predecessor. The target (`emc-vaccine-development-path.md:74,327`) correctly names the ten-allele panel — the guard worked there and missed the sibling. |
| 4 | `realised_spend_omitted_the_selcal_lane` | 0 / 0 | **SILENTLY-INERT** | The retired best estimate **$126.17** is restated as the *current* figure inside `research/manuscripts/pinned-figures.json:1848` and `:1854` — the `current` fields of the two sibling entries — while the live artifact `research/modalities/realised-spend.json` reads `realised_usd_best_estimate = 133.38` (and this entry's own `current` says $133.38). The pattern's alternative is `best estimate is \*\*\$126\.17\*\*` (bold, with "is"); the registry prose writes *"the best estimate $126.17"*, so it cannot fire — and the registry is not a target anyway. This is the `$126.17` current-vs-retired disagreement W28b/W28c/W28d left with the file owner, now located and measured: the retired value survives **inside the registry that retires it**. `$77.28` occurs nowhere. |
| 5 | `aso_standard_practice_excludes_parents` | 0 / 3 | CORRECTLY-INERT | Hits: `pinned-figures.json:1512` (its own pattern) and `research/manuscripts/lint_claims.py:576-577`, a dated rule-rationale comment quoting the retired abstract phrasing as the defect. No live assertion. |
| 6 | `aso_reagent_coverage_95pct` | 0 / 5 | CORRECTLY-INERT | All five are the correction machinery: `aso_reagent_coverage.py:5,154` and `aso/fusion-junction-aso-reagent-coverage.json:3` `_why` fields ("The manuscript claimed…"), plus a sprint mutation record. Live figure is 68.4%. |
| 7 | `thiol_hg_occlusion_first_gen` | 0 / 2 | CORRECTLY-INERT | `research/manuscripts/program/map-audit-strategy.md:239` and `archive/manuscripts/map-audit-manuscript.md:404` both quote the 76% claim inside an audit table whose own **VERDICT** row reads *"STALE — correct value ≈92 %"*. The sole live home (`nr4a3-program-map.md`, a target) is clean. |
| 8 | `single_host_new_card_figures_2026_07_27` | 0 / 28 | CORRECTLY-INERT | Every hit is a raw per-host reading retained as provenance (`vast-bench-sweep-results.json` `ns_per_day`/`_raw` BENCH_RESULT lines, `throughput-bench-provenance.json`) or an unrelated field (`vast-market-offers-raw.json:5783` `dlperf_per_dphtotal`). Independently corroborates W28d's UNTESTABLE reclassification of this entry. |
| 9 | `card_a100pcie_and_3090ti_first_pass_medians` | 0 / 9 | CORRECTLY-INERT | `vast_cost_model.py:169` carries `524.43,  # ** 2 hosts, provisional ** 523.82 / 525.05` — the two per-host draws *behind* the current median. `vast-bench-board-impact.json` is a `utc: 2026-07-27T15:27:01Z` record of that sweep's `added` values. Provenance, not restatement. |
| 10 | `valb_rung_band_8_78_22_28` | 0 / 6,123 | CORRECTLY-INERT | The 6,123 are the bare-numeral vacuity W28d named (`8\.78|22\.28` matches substrings of `28.789`, PDB coordinates, TPM values). Filtered to the retired *construction*, three hits remain — `ternary_vast_launch.py:2893`, `tests/test_ternary_vast_launch.py:532`, `.github/workflows/gpu-ternary-fep-vast.yml:588` — all narrating one past launch decision (*"$17.99 against a $22.28 authorisation"*), which stays true as history. Current rung band ($7.32/$20.74) is asserted nowhere against it. |
| 11 | `ternary_lane_valb_cohort3_rates` | 0 / 0 | CORRECTLY-INERT | `1.528x`/`1.574x` occur nowhere in the tree. `0.005214`/`0.005369` appear only in PLUMED `HILLS` hill-height columns; `vast-board-reprice.json`'s `quote_multiple: 1.574` is a 2026-09-07 offer quote, a different quantity. |
| 12 | `realised_spend_before_orphan_leak` | 0 / 0 | CORRECTLY-INERT | `+$2.31 attested` and `$79.59` occur nowhere; the only `79.59` strings are PDB coordinates and a COLVAR column. |
| 13 | `realised_spend_before_retro_orphan_leak` | 0 / 0 | CORRECTLY-INERT | `+$22.31 attested` and `$99.59` occur nowhere; `99.59` hits are a `signed_percentile`, an unrelated retained abstract, and PDB/COLVAR numerals. |
| 14 | `aso_within_partner_shared_donor_run_three_nt` | 0 / 1 | CORRECTLY-INERT | `aso/fusion-junction-aso-working-record.md:2772` quotes the retired §5.1 sentence inside quotation marks under the heading *"A within-partner figure that was a per-partner figure"*, immediately followed by *"The panel-wide within-partner maximum is **five**"*. Correction record. |
| 15 | `aso_parent_null_half_generic_half_specific` | 0 / 1 | CORRECTLY-INERT | `aso/fusion-junction-aso-paper-redteam-round7.md:156` quotes the apportionment only to state it *"is false in both directions it could be read"*. |
| 16 | `aso_ewsr1_partner_share_wilson_upper_87_8` | 0 / 1 | CORRECTLY-INERT (borderline, flagged) | The live manuscript is correct: `fusion-junction-aso-research-article.md:1528` prints `67.2–87.7%`. The one hit, `redteam-round7.md:292`, is a dated round log describing §4.1 at that moment as giving `67.2–87.8%`; the same document at `:634-635` records the correction. History, but a reader could mistake `:292` for a description of live text. |
| 17 | `aso_canonical_file_condemned_record_count_250` | 0 / 3 | CORRECTLY-INERT | `pinned-figures.json:1938` (own pattern) plus `aso/review-backlog-2026-08-19.md:101-102`, which quotes both retired sentences as backlog item A2 and prescribes 249/252. |
| 18 | `aso_canonical_file_junction_key_count_40` | 0 / 2 | CORRECTLY-INERT | `aso_sequence_manifest.py:810` — *"The block **previously said** … eight of the 40 junctions … Recomputed here: the file keys a row to 43"* — and the same backlog item at `review-backlog-2026-08-19.md:109`. |
| 19 | `vaccine_e7…` → see #3 | | | |
| 20 | `commit_loop_about_75_seconds` | 0 / 9 | CORRECTLY-INERT | The declared home `CLAUDE.md §6` now carries **no** commit-loop timing at all (`grep -nE 'commit loop|130\.7|57\.1|gate 13' CLAUDE.md` → empty). The 9 hits are `research-ledger.json` defect entries quoting the then-live pin and the S6-COMMITLOOP sprint record's `old_value` field. |
| 21 | `commit_loop_gate13_39s_55_tests` | 0 / 7 | CORRECTLY-INERT | Sprint record `old_value` fields, the registry's own pattern, and `scripts/preflight.sh:315-319` under an explicit header *"⚠ Superseded, retained (CLAUDE.md rule 1.2)"*. |
| 22 | `commit_loop_about_nine_minutes` | 0 / 2 | CORRECTLY-INERT | `pinned-figures.json:1999` (own pattern) and `.claude/skills/repo-gates/references/legacy-2026-09-04.md:114`, marked *"⚠ Superseded 2026-09-02, retained (CLAUDE.md rule 1.2)"*. |
| 23 | `commit_loop_gate13_446s_85_to_94_percent` | 0 / 20 | CORRECTLY-INERT (borderline, flagged) | Sprint records and `preflight.sh:310-313` under the explicit "⚠ Superseded, retained" header. ⚠ One unmarked exception: `research/autonomy/stuck_clock.py:374` reads *"about 55% of a gate that is itself 85-94% of the commit loop"* — present tense, no marker — though the enclosing comment block is a dated 2026-09-01 diagnosis in the past tense (*"THE COMMIT LOOP'S SINGLE BIGGEST COST **LIVED** IN THIS FUNCTION"*), and this entry's own `current` sanctions retaining that reading. |
| 24 | `commit_loop_citation_provenance_44s` | 0 / 3 | CORRECTLY-INERT | Two sprint records plus `preflight.sh:312`, inside the same explicitly-marked superseded retention block. |

(Rows are numbered by table position; #19 is the cross-reference for the vaccine entry graded at #3, so the table covers exactly 23 entries.)

### The three findings that matter

1. **One of the 23 is inert inside the gate's own scope, purely from line wrapping** (#1). `check_superseded` is line-oriented; a pattern spanning a soft wrap in a Markdown target can never fire. That is a *class*, not a one-off, and it is the only one of the 23 a scope change could not explain away. (This entry is also the one W28b/W28c flagged as mis-filed — it has `artifact`/`note` and no `current`, and its capture group matches any percentage — so its retired-value identity remains the owner's question; its unreachability is measured regardless.)
2. **Two of the 23 are inert because the retired claim migrated to a sibling manuscript outside `targets[]`** (#2, #3). A statistic the registry calls **withdrawn** is printed as a current result in `fusion-junction-neoantigen-paper.md` and twice in the modality census. This is exactly the hazard W51 measured from the other side ("171 of 187 tracked manuscript `.md` files are outside every rule"), now with a named instance where the *same retired quantity* is loose in an unscanned file.
3. **One retired value survives inside `pinned-figures.json` itself** (#4): `$126.17` is retired by one entry and asserted as current by two others, against a live artifact that says `$133.38`. No consumer compares registry prose against registry prose, so nothing can catch it.

## Validation evidence

All `RUN` in `/home/user/Rare-cancers`, `python3` = `/usr/local/bin/python3`, container Linux 6.18.44, scratch under `/tmp/claude-0/w62/` (deleted). No network, no paid API, no GPU. HEAD `8a674064` → `fcb36d3c` (campaign-directory commits only).

```
$ python3 /tmp/claude-0/w62/inert.py
total 81 inert 23                       # id list identical to W47's 23, entry for entry

$ python3 /tmp/claude-0/w62/scan.py     # 23 compiled patterns x whole tree
scanned files: 7604                     # .git, node_modules, __pycache__, binaries and
                                        # research/autonomy/opus-capacity-campaign-20260908 excluded

$ python3 /tmp/claude-0/w62/verify.py
[aso_thermo_cross_margin_discordance] .../fusion-junction-aso-research-article.md:1167
   per-line match: False | joined-with-prev match: True
[vaccine_e7_coverage_stated_without_a_panel] .../fusion-junction-neoantigen-paper.md:246
   per-line match: False | joined-with-prev match: False
[vaccine_coverage_wilson_intervals] .../fusion-junction-neoantigen-paper.md:246
   per-line match: True  | joined-with-prev match: True
[realised_spend_omitted_the_selcal_lane] research/manuscripts/pinned-figures.json:1848
   per-line match: False | joined-with-prev match: False
targets contains research-article: True
targets contains neoantigen paper: False
targets contains pinned-figures.json: False

$ python3 -c "import json;print(json.load(open('research/modalities/realised-spend.json'))...)"
attested_unledgered_usd = 48.89
realised_usd_best_estimate = 133.38

$ python3 research/manuscripts/lint_consistency.py | tail -2
lint_consistency: 0 ERROR across 29 target file(s)
EXIT=0
```

Plus targeted `grep -rInE` value searches (12 patterns) and `sed -n` reads of 12 context windows, all quoted inline in the Result table.

`PROPOSED (NOT RUN)`: nothing. I authored no repair, patch, gate, test or pattern change, and proposed none as code.

## Limitations

- **The grading rule is a judgement instrument, not a measurement.** The scans (hit sets, file:line, match/no-match) are measured; the CORRECTLY/SILENTLY split rests on reading each occurrence and deciding whether it asserts the value as current. I state the rule explicitly and give the raw hit counts per row so any reader can re-grade a row without re-running anything. Rows #16 and #23 are the two I judge borderline and have flagged as such.
- **Absence of a textual hit is not proof the retired claim is gone**: a claim can be restated in wording neither the pattern nor my value-level greps anticipate. For the six zero-hit entries I searched the retired numerals and the retired constructions, not the space of all paraphrases. Those rows are "no evidence of survival", which is weaker than "gone".
- **Binary files and `results/` trajectory data were scanned as text**; numeral coincidences there (PDB coordinates, PLUMED `HILLS`, COLVAR columns) are the reason several patterns look live and are not.
- I did not test `is_cleared`, did not perturb any file, and did not re-run W28d's transplants or W47's consumer census.
- **This is an instrument audit of a lint registry.** It makes no scientific, EMC efficacy, safety, selectivity or clinical-readiness claim, and says nothing about whether any pinned number is scientifically right. In particular I do not restate any retired value as current: the withdrawn Wilson intervals at #2 and the panel-free coverage sentence at #3 are reported as text present in the tree, not as findings.
- Single HEAD pair; no frozen-corpus cross-read.
- No content-policy refusal occurred.

## Stop condition

Set up front: **stop when all 23 entries carry a grade (CORRECTLY-INERT / SILENTLY-INERT / UNDECIDABLE) supported by a whole-repository search for the retired value plus a read of the entry's `current` and supersession record, with every SILENTLY-INERT row quoted at file:line and re-confirmed against the real compiled pattern — or at ~40 tool calls / ~40 minutes.**

**MET.** 23 of 23 graded; 19 / 4 / 0; all four SILENTLY-INERT rows quoted and re-confirmed with a match control. Returned immediately.

## Tool-call and wall-clock count actually used

**9 tool calls** (all Bash, several carrying two independent commands), against a ~40 target. **Wall clock 04:48:04Z → 04:54:27Z = 6 min 23 s**, against a ~40 min target.

## Next concrete action

One bounded successor, for the owner of `lint_consistency.py` and the manuscripts named — **not** authored here and requiring no repository write to decide:

**Route the four SILENTLY-INERT rows individually, because they have three different causes and only one is a linter question.**
1. `aso_thermo_cross_margin_discordance` — a **line-oriented-matching** defect: a target-file sentence unreachable because it soft-wraps. The correct successor is to measure how many of the 81 patterns contain a whitespace run that could straddle a wrap in a target (a scan, not a repair), before anyone changes matching semantics; widening `\s+` to cross lines would change 81 guards at once.
2. `vaccine_coverage_wilson_intervals` and `vaccine_e7_coverage_stated_without_a_panel` — a **scope** question for the vaccine-path owner: a withdrawn statistic and a panel-free coverage sentence are live in `fusion-junction-neoantigen-paper.md` and the modality census, which no rule scans. Whether those files should join `targets[]` is a human decision with a real cost (W51: 171 of 187 manuscript files are out of scope by design).
3. `realised_spend_omitted_the_selcal_lane` — a **registry-internal contradiction** for the file owner: `$126.17` is retired by one entry and asserted as current by two, against a live artifact reading `$133.38`. This is the disagreement W28b/W28c/W28d each declined to litigate; it is now located to `pinned-figures.json:1848` and `:1854` with the artifact value measured.

And the standing caution this run confirms, for whoever acts on W47's alarm proposal: **19 of the 23 are inert for the right reason**, so a blanket ERROR on zero-match superseded entries would redden the gate on 19 correct rows to surface 4 — exactly the tradeoff W47 warned about. A WARN-level census that prints the 23 with their repo-wide hit counts would have surfaced all four of these without touching a single passing gate.
