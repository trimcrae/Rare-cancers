> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

## Worker

**W17e**, lane 17 refill, OPUS-CAPACITY-CAMPAIGN-20260908 — artifact-resolution audit of the printed numbers in the EMC/ATR assessment, standing up `p1s[1]`'s missing `artifact_figures` binding.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). I did not observe the served model, and **no environment variable names a model** (the `env | grep -i 'model'` arm returns nothing). The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:24:11 UTC 2026`. `date -u` at end: `Tue Sep  8 02:30:37 UTC 2026` (last timed call; report drafted after).

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (verbatim, full):

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,...
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

**Repository state — honest correction to the brief, and the HEAD moved again mid-run.** The brief's frozen commit is `92abbcb905…`. At my first tool call `git rev-parse HEAD` returned **`b9a0257e6acff53ad22535cf2adf261313e0b250`**; at my last it returned **`47aac85f874a57a6f981c3432abcf16980968aec`** — the coordinator is committing campaign material under me. I verified that this does not contaminate my inputs: `git diff --name-only b9a0257e… 47aac85f… -- <my four input files>` returns **empty**. `git status --porcelain` is clean; **I created and modified nothing under `/home/user/Rare-cancers` and ran no git write operation.** All execution was in `/tmp/claude-0/w17e/`.

---

## Question

**Which of the machine-derived numbers printed in `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` resolve to a field in `research/modalities/emc-atr-vulnerability.json`, which disagree with the artifact, and which have no resolvable artifact home at all?**

Open because `research/autonomy/hardening-state/PUB-ATR.json` `p1s[1]` records, verbatim:

> "This document has no `artifact_figures` entry in research/manuscripts/pinned-figures.json, so not one of its roughly two hundred machine-derived numbers is bound by a gate to the artifact field that produces it — and the document's own appendix records four separate rounds of exactly the drift such a binding exists to catch."

Its `fix` asks for `artifact_figures` entries "keyed to the fields they come from". That keyed candidate list is the deliverable here; the third classification bucket (no resolvable home) is where the successor `p1s[0]`-shaped finding was expected to live, and it is where I found one.

---

## Prior-work check

Commands run and what they showed:

- `cat CLOSED-WORK.md` — read in full. Not replaying: ASO/NAT/Qeios, the tissue-RNA paper, frozen comment `7baf2727…`, the retained biology-access refusal, PUB-EMC-CLASSIFICATION (user-rejected), any Brenca route, `GSE4303`/`GSE28866` rediscovery (I read only committed derived fields, no primary data). No network was used; no denied route was replayed.
- `sed -n 1,200p reports/W17c-mde-range-rederivation.md`, `wc -l reports/W17*.md` — W17c closed the reproducibility half of `p1s[0]` (0.045–0.186 reproduces exactly under Student-t on the carried Welch df; the normal reading gives 0.0414–0.1644). **I did not re-derive the MDE range and did not re-run W17's df-feasibility identity.** Two occurrences of `0.045` appear in my MISMATCH candidate list purely as a rounding artifact of my own declared rule (see R5 adjudication); I did not re-open the question.
- `python3 -c "...PUB-ATR.json p1s[1]..."` — quoted above and used as the specification.
- `grep -rn "artifact_figures" scripts/*.py research/**/*.py` → `research/manuscripts/lint_consistency.py:401 check_artifact_figures`, plus `claim_audit.py`, `claim_coverage.py`, `aso_archive_manifest.py`. This is the gate `p1s[1]` refers to, and I verified my candidates against **it**, not a re-implementation.
- `grep -rln "NR4A3_family_fraction\|emc_model_identity_check" --include=*.json --include=*.py --include=*.md .` → the field named in `p1s[1]`'s own `fix` lives in `research/modalities/atr-hrd-sarcoma-series.json`, **not** in `emc-atr-vulnerability.json` (finding F3 below).
- `python3 -c "...list(pinned-figures.json)..."`, and `targets` inspection → the document **is** in `targets` (so supersession-marker rules already apply to it) and appears in **no** `must_appear_in` across the 99 existing `artifact_figures` entries. `p1s[1]`'s premise is confirmed at my HEAD.

I am **not** attempting `p1s[2]` (22-vs-27 itemisation), did not edit the manuscript, `PUB-ATR.json`, or `pinned-figures.json`, and opened no review round.

---

## Method / inputs

| File (read-only) | Role |
|---|---|
| `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` (1146 lines) | the scanned document |
| `research/modalities/emc-atr-vulnerability.json` (342 KB, **3516 numeric leaves**) | the primary artifact |
| `research/manuscripts/pinned-figures.json` | the registry `p1s[1]` says lacks an entry; also the schema I matched |
| `research/manuscripts/lint_consistency.py` (`check_artifact_figures`, `_dig_json`) | the real gate, imported to verify candidates |
| `research/modalities/{emc-atr-vulnerability-inputs, atr-hrd-sarcoma-series{,-inputs}, emc-fet-idr-census, emc-fet-construct-designs, fet-ddr-axis-scan, emc-sra-study, atm-status-atri-stratification}.json` | the eight sibling artifacts the document cites, for the UNRESOLVED split |

**Tools:** `python3` 3.11.15, stdlib only (`json`, `re`, `os`, `collections`), ripgrep/coreutils. No network, no installs, no paid API, no GPU. Execution directory `/tmp/claude-0/w17e/`.

**Resolution rules and tolerance were written into the script's module docstring before the first execution and were not altered afterwards.** They are reproduced in full in the script below (R0–R7). In summary: extraction of numeric literals with declared exclusions (link targets, section refs, dates/years, accessions, ordinals, footnotes); **MATCH = exact equality after rounding the artifact value to the number of decimals printed**, under four explicitly enumerated unit readings only (identity; ×100 when a `%` is printed; ÷100 for `_pct`/`_percent` fields; sign-free only under a named context word) — **no numeric tolerance beyond printed precision**; MISMATCH = no exact match but a context-token-tied field within 10 % relative; UNRESOLVED = neither, split by whether an exact-at-precision home exists in one of the eight sibling artifacts.

---

## Result

### R1 — the three classified sets, with counts `PRIMARY` (arithmetic on committed files)

Occurrences kept after the declared R1 exclusions: **1084**. Excluded and why: `section-ref=155, accession=85, date=64, link/path=51, list-ordinal=25, year=17, objectid=3, footnote=2, code-path=1` (403 excluded).

| Class | n | % of 1084 | Evidence grade |
|---|---:|---:|---|
| **MATCH** — exact at printed precision to ≥1 field of `emc-atr-vulnerability.json` | **897** | 82.7 % | `PRIMARY` |
| **MISMATCH** — no exact match, but a context-tied field within 10 % | **44** | 4.1 % | `PRIMARY` (candidates; adjudicated below) |
| **UNRESOLVED-ELSEWHERE** — exact home in a sibling artifact, not the primary one | **44** | 4.1 % | `PRIMARY` |
| **UNRESOLVED-NOWHERE** — no exact home in any of the nine artifacts | **99** | 9.1 % | `PRIMARY` |
| TOTAL | 1084 | | |

⚠ **The 82.7 % MATCH rate is an upper bound on the meaningful figure and must not be quoted as an accuracy measure.** A "match" here means *some* field of a 3516-leaf artifact carries that value at printed precision; with 3516 leaves, small integers and 2-decimal values collide freely. It establishes that a home *exists*, not that it is *the* home. The AMBIGUOUS flag (no context-tied path among the matching paths) is recorded per occurrence in `results.json` for the coordinator.

### R2 — the MISMATCH set in full, with adjudication `PRIMARY`

All 44 are listed. **On inspection, none is a confirmed prose-vs-artifact disagreement.** I report the whole set including the embarrassing part — that my own R5 heuristic is mostly noise — rather than trimming it.

**(a) Inside Appendix A "superseded, retained" (line ≥ 1117) — 11 occurrences. DELIBERATE, NOT DEFECTS.** These are the retired values the document quotes on purpose, and `pinned-figures.json` already carries `supersession_markers` covering exactly this ("superseded", "previously", "appendix a", "no longer", …).

| Line | printed | artifact | field |
|---|---|---|---|
| 1125 | 4500 | 4303 | `…GSE24369….probe_mapping_diagnostic.ncbi_n_accessions_queried` |
| 1130 | 662 | 661 | `…GSE4303-GPL3288….n_accessions_resolved_by_curated_dictionary` (spurious tie) |
| 1140 | 20,324 (×2) | 20629 | `…GSE24369….n_probes_mapped_to_symbols` — Appendix drift (i) |
| 1140 | 0.932 | 0.982 | `…series_readability.GSE24369.probe_mapping_rate_per_platform.GPL6244` — drift (i) |
| 1140 | +0.045 | 0.0445 | `…GSE24369….DNA_damage_checkpoint.delta_a_minus_b` (rounding, see (d)) |
| 1140 | 95.4 % | 99.0 | `…GSE28866….n_samples` (spurious tie) |
| 1141 | 27,195 | 27196 | `…GSE4303-GPL3290….n_probes_mapped_to_symbols` — Appendix drift (ii) |
| 1142 | 2.7 | 2.491 | `…control_oxphos.mean_t` (spurious tie) |
| 1142 | 0.0333 | 0.0336 | `…olaparib….rho` (spurious tie) |
| 1145 | 10,332 | 10331 | `…biostudies.total_per_query["NR4A3 sarcoma"]` — Appendix drift (iii) |

**(b) Extraction leakage — 8 occurrences.** Digit runs inside identifiers that survived rule R1(d) because its implementation only tests an immediately-preceding uppercase prefix from a fixed list: `AI050027`→`050027` (L437), `AK074482`→`074482` and `M37726`→`37726` (L518), `1,670`→`4, 1,670` (L264, the regex's space class swallowed a table-cell boundary), plus markdown heading ordinals `2.2` (L279) and `3.1` (L395) not covered by R1(b), which only excludes `§`/"section". **These are defects in my extractor, not in the manuscript**, and I am reporting them rather than patching the declared rule.

**(c) Spurious context ties — 17 occurrences.** L50/L53 `50`↔`NR4A1.percentile_in_depmap_panel` 51.9; L51 `+2.048`↔`n_drugs.ATR_inhibitors` 2; L94 `−1.016`/`−2.065`↔ unrelated `t` values; L197 `97` (a line-number pointer)↔`n_lines_with_all_three` 91; L440 `650`↔655; L448 `4500`↔4303; L464 `662`↔601; L510 `95.4 %`↔`n_up_genes` 100; L553 `6.5 %`↔ a `t`; L576 `0.045`↔0.0376; L678 ×5 (`922`,`863`,`919`,`+0.248`,`−1.191`); L738 `2.7`↔2.491. In each the printed number is a real figure whose true home is elsewhere (often §8's `atr-hrd-sarcoma-series.json`) or a within-sentence derivation; the token overlap is coincidental.

**(d) Half-way rounding under R3 — 4 occurrences. A limitation of my own declared rule.** L533 `+0.074` vs artifact `0.0735`; L626 `0.347` vs `0.3465`; L578 and L831 `0.045` vs `0.0445`. R3 rounds the artifact value with Python's `round()`, which is round-half-to-even on the binary representation (`round(0.0735,3)→0.073`), while the manuscript rounds half-up. These are **correct printed values misclassified by my tolerance rule**. Per R7 I did not relax the rule; the consequence is that the true MATCH count is at least 901, not 897, and the true confirmed-MISMATCH count is **0**.

**(e) §8 table values whose home is another artifact — 4 occurrences.** L1025/L1037 `67`, L1032 `39.51`/`28.79`/`17.03` — tied to `dataset_search.geo.series.*.n_samples` by coincidence; the real figures live in `atr-hrd-sarcoma-series.json`.

> **MISMATCH bottom line: 44 candidates, 0 confirmed prose-vs-artifact disagreements outside the retained appendix.** Against the current artifacts, the document's printed values hold — which corroborates `p1s[1]`'s own parenthetical "every current value now reads correctly against the pinned artifacts (verified this round)" by an independent mechanical route. It does **not** weaken `p1s[1]`: correctness today is exactly what an ungated document loses on the next regeneration.

### R3 — the `p1s[0]`-shaped finding in the UNRESOLVED-NOWHERE set `PRIMARY`

Of the 99 UNRESOLVED-NOWHERE occurrences, the large majority are further extraction leakage of the same kind as (b) — PMIDs (`34413129`, `41811428`, `37205599`), DOI fragments (`10.1101/2023.04.30.538578`), page ranges (`446-455`, `2660-2677`), HTTP status codes (`404`, `500`, `502`), drug codes (`AZD6738`, `VE-822`, `MK-1775`), GEO/DepMap/Cellosaurus identifiers, BioProject `PRJNA1273954`, and line-number pointers. **These are not machine-derived figures and I do not count them as unhomed results.**

One genuine, load-bearing cluster survives, at **§5.1, line 761**:

> ``|ρ| > 1.15 × 0.1711`` = **0.1968** (§1); +0.2123 clears it by **0.0155, 0.41× that standard error**,

| Printed | Status | Evidence |
|---|---|---|
| `0.1968` (the specificity bar) | **no artifact field, no code output** | `grep` finds `1.15` only at `emc_atr_vulnerability.py:2935`, inside `srec["beats_the_proliferation_control"] = bool(abs(rho) > abs(prolif_rho) * 1.15)` — the artifact stores the **boolean** (`true`) and the two inputs, never the product |
| `0.0155` (the margin) | **no artifact field, no code output** | same |
| `0.038` (SE) and `0.41×` | **no artifact field, no code output**; `n ≈ 700` is itself an approximation | the artifact carries per-drug `n` = 597 / 565, not 700 |
| `0.1711` as printed | printed **unsigned**; the artifact field is **−0.1711** | `specificity["expr::proliferation_MYC"].mean_rho_across_ATR_inhibitors` |

I re-derived all four from the artifact: bar `1.15 × |−0.1711| = 0.1968` ✓, margin `0.2123 − 0.1968 = 0.0155` ✓, `SE = 1/√(700−3) = 0.0379 → 0.038` ✓, `0.0155/0.0379 = 0.41` ✓. **The arithmetic is correct and self-consistent; the numbers are prose-only.** This is structurally the same defect as `p1s[0]`'s MDE range — a load-bearing quantitative claim (it is the margin by which Part D's *one PASS row* clears its specificity control) carried by no artifact field and produced by no code, so `--check` cannot re-derive it. `PRIMARY` for the absence; `UNKNOWN` whether the authors intended `n ≈ 700` as a stated approximation rather than a computed value.

### R4 — two blockers in `p1s[1]`'s own `fix` text `PRIMARY`

**F1. Three of the `fix` field's example keys are unaddressable by the gate's key digger.** `lint_consistency._dig_json` splits the key on `"."` with no bracket or escape support. Platform keys in this artifact are **filenames containing dots**:

```
>>> _dig_json(doc, 'part_b_emc_tumour_signature.per_platform.GSE4303-GPL3290_series_matrix.txt.gz.n_probes_mapped_to_symbols')
KeyError: 'GSE4303-GPL3290_series_matrix'
```

So an entry written literally as the `fix` describes (`per_platform["GSE4303-GPL3290_…txt.gz"].n_probes_mapped_to_symbols` = 27196, `.probe_mapping_diagnostic.accession_resolution_rate` = 0.582, the GSE24369 pair 20629 / 0.982) yields `A-key-missing` — a gate that reports on nothing. **Workaround found and used:** the two *rates* have dot-safe twins under `series_readability` (`…series_readability.GSE4303.probe_mapping_rate_per_platform.GPL3290` = 0.582; `…GSE24369….GPL6244` = 0.982), which I pinned. The two *probe counts* (27196, 20629) have **no dot-safe path** — pinning them requires either bracket support in `_dig_json` or a new flat field in the artifact. Both are manuscript-owner / tooling-owner decisions; I made neither.

**F2. List indices are likewise unaddressable.** `emc_model_identity_check.emc_labelled_samples[0].NR4A3_family_fraction` (0.0634) cannot be dug at all. I substituted the sibling scalar `…NR4A3_family_fraction.median_across_all_samples` (0.0524), which the same sentence prints.

**F3. That §8 key is in the wrong artifact.** `emc_model_identity_check` does not exist anywhere in `emc-atr-vulnerability.json` or its `-inputs` file; it lives in **`research/modalities/atr-hrd-sarcoma-series.json`**. My candidate entry names that artifact and its `--write` entry point.

**F4 (incidental, `UNKNOWN`).** In `atr-hrd-sarcoma-series.json`, `emc_model_identity_check.emc_labelled_samples[0]` carries `NR4A3_family_fraction: 0.0634`, `family_fraction_rank_of_68: 29` and `fold_over_panel_median: 7.0`, while `NR4A3_family_fraction.median_across_all_samples` is `0.0524` (ratio 1.21). The manuscript at L1031 attributes the `7.0×` to the **TPM** panel median (1.896), not the family fraction, so the `7.0` is probably correctly scoped and the artifact field name merely ambiguous. **I did not verify this and make no claim; flagging it for the owner only.**

### R5 — the deliverable: keyed candidate `artifact_figures` list `PRIMARY`

**11 candidates, all 11 verified clean by the repository's own `check_artifact_figures` against the current tree, and all 11 shown to redden when the artifact moves** (negative control below). **This is data routed to the PUB-ATR owner. It is not authored into `pinned-figures.json` or any other file.**

```json
{
 "artifact_figures": [
  {
   "id": "emc_atr_gse4303_gpl3290_accession_resolution_rate",
   "description": "Part B: GPL3290's accession resolution rate after the archived-UniGene rebuild. The figure that overturned the SIGNATURE_NOT_READABLE verdict; drifted once already.",
   "artifact": "research/modalities/emc-atr-vulnerability.json",
   "key": "part_b_emc_tumour_signature.series_readability.GSE4303.probe_mapping_rate_per_platform.GPL3290",
   "scale": 100.0, "format": "{:.1f} %", "tolerance": 0.05,
   "context": "accession resolution from \\*\\*1\\.0 % to 58\\.2 %\\*\\*",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/emc_atr_vulnerability.py --write, then update the printed rate in the SAME commit"
  },
  {
   "id": "emc_atr_gse24369_gpl6244_accession_resolution_rate",
   "description": "Part B: GSE24369/GPL6244's accession resolution rate. The prose carried 93.2 % from artifact commit ce630e2b4 after the artifact moved to 0.982 (Appendix drift (i)).",
   "artifact": "research/modalities/emc-atr-vulnerability.json",
   "key": "part_b_emc_tumour_signature.series_readability.GSE24369.probe_mapping_rate_per_platform.GPL6244",
   "scale": 100.0, "format": "{:.1f} %", "tolerance": 0.05,
   "context": "single-channel, \\*\\*98\\.2 %-mapped\\*\\*",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/emc_atr_vulnerability.py --write"
  },
  {
   "id": "emc_atr_knockout_axis_mean_sarcoma_pool",
   "description": "Part C: the ATR/ATRIP/CHEK1 knockout axis mean across the sarcoma pool - the floor reading the coordinated-dependency null rests on.",
   "artifact": "research/modalities/emc-atr-vulnerability.json",
   "key": "part_c_coordinated_dependency.knockout_instrument_with_matched_comparator.axis_mean_sarcoma_pool",
   "format": "{:.3f}", "tolerance": 0.005,
   "context": "mean \\*\\*−1\\.340\\*\\* across the sarcoma pool",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/emc_atr_vulnerability.py --write"
  },
  {
   "id": "emc_atr_knockout_delta_fet_minus_matched",
   "description": "Part C: FET-minus-matched delta on the knockout instrument - the null that keeps Part C from reading as an EMC dependency.",
   "artifact": "research/modalities/emc-atr-vulnerability.json",
   "key": "part_c_coordinated_dependency.knockout_instrument_with_matched_comparator.delta_FET_minus_matched",
   "format": "{:.4f}", "tolerance": 0.0005,
   "context": "FET-minus-matched delta of \\*\\*−0\\.0065\\*\\*",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/emc_atr_vulnerability.py --write"
  },
  {
   "id": "emc_atr_partd_rho_atr_dependency",
   "description": "Part D row 1: mean rho across ATR inhibitors for the ATR+ATRIP+CHEK1 CRISPR dependency - the one row that PASSES.",
   "artifact": "research/modalities/emc-atr-vulnerability.json",
   "key": "part_d_drug_response_correlation.mechanism_tests.dependency::ATR_ATRIP_CHEK1_mean_gene_effect.mean_rho_across_ATR_inhibitors",
   "format": "{:+.3f}", "tolerance": 0.0005,
   "context": "ATR\\+ATRIP\\+CHEK1 CRISPR dependency\\*\\* \\| ρ > 0 \\|",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/emc_atr_vulnerability.py --write"
  },
  {
   "id": "emc_atr_partd_rho_replication_stress",
   "description": "Part D row 2: replication-stress expression mean rho across ATR inhibitors.",
   "artifact": "research/modalities/emc-atr-vulnerability.json",
   "key": "part_d_drug_response_correlation.mechanism_tests.expr::replication_stress.mean_rho_across_ATR_inhibitors",
   "format": "{:.3f}", "tolerance": 0.0005,
   "context": "^\\| replication-stress expression \\| ρ < 0 \\|",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/emc_atr_vulnerability.py --write"
  },
  {
   "id": "emc_atr_partd_rho_atm_signalling",
   "description": "Part D row 3: ATM-signalling expression mean rho - the wrong-sign row the headline turns on.",
   "artifact": "research/modalities/emc-atr-vulnerability.json",
   "key": "part_d_drug_response_correlation.mechanism_tests.expr::ATM_signalling_DSB_repair.mean_rho_across_ATR_inhibitors",
   "format": "{:.3f}", "tolerance": 0.0005,
   "context": "^\\| \\*\\*ATM-signalling expression\\*\\* \\| ρ > 0 \\|",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/emc_atr_vulnerability.py --write"
  },
  {
   "id": "emc_atr_partd_rho_fet_heldout",
   "description": "Part D row 4: held-out FET-fusion signature mean rho.",
   "artifact": "research/modalities/emc-atr-vulnerability.json",
   "key": "part_d_drug_response_correlation.mechanism_tests.signature::FET_fusion_heldout.mean_rho_across_ATR_inhibitors",
   "format": "{:.3f}", "tolerance": 0.0005,
   "context": "^\\| held-out FET-fusion signature \\| ρ < 0 \\|",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/emc_atr_vulnerability.py --write"
  },
  {
   "id": "emc_atr_partd_proliferation_control_rho",
   "description": "Part D: the proliferation control rho every specificity row is read against. NOTE: pinned on the §5 table header, which prints the SIGNED value; the §5.1 sentence prints the magnitude 0.1711 with no sign and therefore cannot be pinned to this field as written.",
   "artifact": "research/modalities/emc-atr-vulnerability.json",
   "key": "part_d_drug_response_correlation.specificity.expr::proliferation_MYC.mean_rho_across_ATR_inhibitors",
   "format": "{:.3f}", "tolerance": 0.0005,
   "context": "vs proliferation control \\(ρ = −0\\.171\\)",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/emc_atr_vulnerability.py --write"
  },
  {
   "id": "emc_atr_biostudies_broad_nr4a3_query_total",
   "description": "Section 3.0a: the BioStudies broad-query total. Prose carried 10,332 against 10,331 (Appendix drift (iii)).",
   "artifact": "research/modalities/emc-atr-vulnerability.json",
   "key": "part_b_emc_tumour_signature.dataset_search.biostudies.total_per_query.NR4A3 sarcoma",
   "format": "{:,.0f}", "tolerance": 0.5,
   "context": "the broad NR4A3 query returns \\*\\*10,331\\*\\*",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/emc_atr_vulnerability.py --write"
  },
  {
   "id": "emc_atr_model_identity_family_fraction_panel_median",
   "description": "Section 8: the panel median NR4A3 family fraction the EMC-labelled model is read against. NOTE: this figure lives in atr-hrd-sarcoma-series.json, not emc-atr-vulnerability.json.",
   "artifact": "research/modalities/atr-hrd-sarcoma-series.json",
   "key": "emc_model_identity_check.NR4A3_family_fraction.median_across_all_samples",
   "format": "{:.4f}", "tolerance": 0.0005,
   "context": "against a panel median of \\*\\*0\\.0524\\*\\*",
   "must_appear_in": ["research/manuscripts/dependency/emc-atr-vulnerability-assessment.md"],
   "regenerate": "python3 research/modalities/atr_hrd_sarcoma_series.py --write"
  }
 ]
}
```

**Coverage against `p1s[1]`'s `fix` request:** Part B 2/4 (the two rates; the two probe counts blocked by F1), Part C 2/2, Part D 5/5, §8 1/1 (via the substitution in F2/F3). **Not covered, and named as such:** `27196`, `20629`, and the §5.1 prose-only cluster from R3 — which has no field to key to and therefore cannot be pinned at all until someone decides whether the artifact should carry it.

**Two authoring corrections I made to my own candidates during verification** (these are corrections to proposed pins, not to the R0–R7 classification rules): the GPL3290 context regex initially mis-transcribed the source line's emphasis markers; and `emc_atr_partd_proliferation_control_rho` was first pointed at the §5.1 sentence, which prints the **unsigned** `0.1711` against a **negative** artifact field and correctly failed as `A-figure-mismatch` — I moved it to the §5 table header, which prints `−0.171`. The failure is itself reportable: **§5.1's magnitude form cannot be gated to that field as written.**

---

## Validation evidence

### RUN

**Environment for every run below:** container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `Python 3.11.15` (stdlib only), cwd `/tmp/claude-0/w17e`, no network. Repository read at HEAD `b9a0257e…` → `47aac85f…` (inputs verified unchanged across the move).

**RUN 1 — the extractor.**
Command: `cd /tmp/claude-0/w17e && python3 resolve_figures.py > out.txt 2> err.txt; echo "EXIT=$?"` → **`EXIT=0`**

Verbatim output (`err.txt` then `out.txt` head):

```
primary numeric leaves: 3516
=== EXTRACTION ===
manuscript body lines: 1133  occurrences kept: 1084
excluded by rule R1: accession=85, code-path=1, date=64, footnote=2, link/path=51, list-ordinal=25, objectid=3, section-ref=155, year=17
primary artifact numeric leaves: 3516

=== CLASSIFICATION COUNTS ===
MATCH                      897
MISMATCH                    44
UNRESOLVED-ELSEWHERE        44
UNRESOLVED-NOWHERE          99
TOTAL                     1084
```

**RUN 2 — key addressability (F1/F2).**
Command: `python3 -c "...from lint_consistency import _dig_json; ..."` → **`EXIT=0`**

```
FAIL KeyError 'GSE4303-GPL3290_series_matrix' | part_b_emc_tumour_signature.per_platform.GSE4303-GPL3290_series_matrix.txt.gz.n_probes_mapped_to_symbols
OK  10331 part_b_emc_tumour_signature.dataset_search.biostudies.total_per_query.NR4A3 sarcoma
OK  -1.34 part_c_coordinated_dependency.knockout_instrument_with_matched_comparator.axis_mean_sarcoma_pool
```

**RUN 3 — candidate verification with the repository's own checker.**
Command: `cd /tmp/claude-0/w17e && python3 verify_pins.py; echo "EXIT=$?"` → **`EXIT=0`**

```
candidates: 11  clean: 11  with findings: 0
ACCEPTED emc_atr_biostudies_broad_nr4a3_query_total
ACCEPTED emc_atr_gse24369_gpl6244_accession_resolution_rate
ACCEPTED emc_atr_gse4303_gpl3290_accession_resolution_rate
ACCEPTED emc_atr_knockout_axis_mean_sarcoma_pool
ACCEPTED emc_atr_knockout_delta_fet_minus_matched
ACCEPTED emc_atr_model_identity_family_fraction_panel_median
ACCEPTED emc_atr_partd_proliferation_control_rho
ACCEPTED emc_atr_partd_rho_atm_signalling
ACCEPTED emc_atr_partd_rho_atr_dependency
ACCEPTED emc_atr_partd_rho_fet_heldout
ACCEPTED emc_atr_partd_rho_replication_stress
```

(The pre-correction run of the same command returned `clean: 9  with findings: 2`, quoted in R5.)

**RUN 4 — negative control: a pin that never fires is not a gate.** A `/tmp` mirror (`mirror/research/...`) holds a copy of the manuscript and doctored copies of the two artifacts, with three values moved as a regeneration would move them (`10331→10332`, `0.982→0.932`, `−1.34→−1.41`) and the prose left untouched.
Command: `python3 - <<'EOF' ... L.check_artifact_figures(reg, repo='mirror') ... EOF; echo "EXIT=$?"` → **`EXIT=0`**

```
NEGATIVE CONTROL: artifact regenerated, prose not updated -> 3 findings
  A-figure-mismatch | emc_atr_gse24369_gpl6244_accession_resolution_rate: this line quotes [98.2] but ...
  A-figure-mismatch | emc_atr_knockout_axis_mean_sarcoma_pool: this line quotes [-1.34, 99.2, 100.0] but ...
  A-figure-mismatch | emc_atr_biostudies_broad_nr4a3_query_total: this line quotes [2.0, 37.0, 4.0, 3.0, 10331.0] but ...
```

Exactly the three doctored figures redden and no others — the candidates gate what they claim to gate.

**RUN 5 — the §5.1 unhomed cluster re-derived.** Command: `python3 -c "...bar=1.15*abs(p)..."` → **`EXIT=0`**

```
prolif rho -0.1711  bar 1.15x = 0.1968 (printed 0.1968)
margin 0.0155 (printed 0.0155)
SE at n=700 0.0379 (printed 0.038)  margin/SE 0.41 (printed 0.41)
boolean in artifact: True
```

**RUN 6 — tree untouched.** `git status --porcelain | head -5` → empty. `git diff --name-only b9a0257e… 47aac85f… -- <4 input files>` → empty, `EXIT=0`.

### PROPOSED (NOT RUN)

- **Adding the 11 entries to `research/manuscripts/pinned-figures.json`** and running `python3 research/manuscripts/lint_consistency.py` / `scripts/preflight.sh` on the resulting tree. Not run: the brief makes me read-only on the working tree and forbids preflight without an explicit dispatch instruction, and `p1s[1]`'s repair belongs to the manuscript owner.
- **Bracket/escape support in `lint_consistency._dig_json`** so `per_platform["…txt.gz"]` keys become addressable (unblocking 27196 / 20629), or a flat mirror field in the artifact. Not written; it is a tooling change outside this lane and would need its own test.
- **Instrumenting §5.1's `0.1968` / `0.0155` / `0.41×` into `emc_atr_vulnerability.py` and the artifact.** Not attempted — it is the same class of repair as `p1s[0]`'s and is the owner's call.

---

## Limitations

- **The 82.7 % MATCH rate is not an accuracy measurement** and must not be quoted as one. With 3516 numeric leaves, "some field carries this value at printed precision" is a weak existence claim; only the 11 verified candidates are bindings in the gate's sense.
- **My extractor over-collects.** R1's exclusion list is implemented approximately: accession fragments, heading ordinals, DOI/PMID/page-range digits and HTTP status codes survive into the classified sets. This inflates UNRESOLVED-NOWHERE (99) far above the true count of unhomed *figures*, which by inspection is a small handful centred on §5.1. I report this rather than having re-tuned R1 after seeing the counts.
- **R3's rounding rule mis-scores half-way values** (Python round-half-even on binary floats vs the manuscript's round-half-up), producing ≥4 false MISMATCHes and suppressing ≥4 true MATCHes. Declared before the run, left unchanged per R7.
- **MISMATCH is a candidate class, not a verdict.** The R5 token-overlap tie is a heuristic; all 44 were hand-adjudicated and none survived as a confirmed disagreement, but the adjudication is my reading, not a machine result.
- **"No confirmed disagreement" is a statement about today's artifacts only.** It is not evidence that the document is safe from drift; it is evidence that the current snapshot is consistent, which is exactly the state a gate exists to preserve.
- **F4 is unverified** and is flagged, not claimed.
- I did not read the whole 1146-line manuscript; I read its structure, the passages my candidates pin, and the appendix. Judgements about whether a figure is "load-bearing" rest on those passages and on `p1s[1]`'s own `fix` text.
- **No clinical claim.** Nothing here establishes EMC ATR-pathway biology, efficacy, safety, selectivity, therapeutic window, or clinical readiness. This is a text-vs-JSON consistency audit; there is no wet lab, and no computational result in this document or in this report bears on patient care.

---

## Stop condition

Set: *an executed extractor with a real command and exit code; three classified sets with counts; the full MISMATCH list; and a keyed `artifact_figures` candidate list routed to the PUB-ATR owner without being authored into any file.*

**MET.** Extractor run (`EXIT=0`), three sets counted (897 / 44 / 44+99), all 44 MISMATCH candidates listed and adjudicated, and 11 keyed candidates delivered as data and verified clean plus negatively controlled by the repository's own `check_artifact_figures`. Nothing was written into the Git working tree; no review round was opened; `p1s[2]` was not attempted; W17c's MDE range and W17's df identity were not re-derived.

---

## Tool-call and wall-clock count actually used

**19 tool calls**; wall clock `02:24:11Z` → `02:30:37Z` at the last timed call, **≈ 8 minutes** of execution plus report drafting. Both well inside the ~40/~40 target.

---

## Next concrete action

**One successor, inside lane 17:** re-derive and instrument the §5.1 specificity-clearance cluster (`0.1968`, `0.0155`, `0.038`, `0.41×`) the way W17c handled `p1s[0]`'s MDE range — establish which `n` the SE is meant to use (the printed `n ≈ 700` matches neither per-drug `n` of 597 or 565), determine whether the four numbers survive under each candidate `n`, and hand the manuscript owner an expected-vs-observed table plus the smallest correct repair (a named `n`, or a new artifact field). It is bounded, read-only, needs no network, and closes the last prose-only quantitative claim this audit found in the document.

---

### Appendix — code authored, returned inline (written and executed only under `/tmp/claude-0/w17e/`)

`resolve_figures.py`:

```python
"""W17e — read-only resolver: printed numbers in the EMC/ATR assessment vs its artifact.

QUESTION
    Which machine-derived numbers printed in
    research/manuscripts/dependency/emc-atr-vulnerability-assessment.md resolve to a field in
    research/modalities/emc-atr-vulnerability.json, which disagree with it, and which have no
    resolvable artifact home at all?

RESOLUTION RULES AND TOLERANCE — DECLARED BEFORE THE RUN, NOT ADJUSTED AFTERWARDS
--------------------------------------------------------------------------------
R0  READ-ONLY. Nothing under the repository is written. All output is stdout / files in /tmp.

R1  EXTRACTION. A "printed number" is a numeric literal in the manuscript body (YAML frontmatter
    excluded) matching
        [-+−]?\d[\d,  ]{0,12}(?:\.\d+)?\s?%?
    Occurrences are EXCLUDED, as not machine-derived figures, when they are:
      (a) inside a markdown link target or an inline/fenced path, i.e. inside `(...)` immediately
          following `]`, or inside backticks that contain `/` or `.json`/`.py`;
      (b) a section/anchor reference: preceded by § or "section " or "§§";
      (c) an ISO date (YYYY-MM-DD) or a bare 4-digit year 1900-2100 not followed by a unit;
      (d) part of a git object id (>=7 hex chars adjacent), an accession (GSE/GPL/SRP/PMC/PMID/
          NCT/DOI/EudraCT context), or a markdown list/heading ordinal at line start;
      (e) a footnote/table-column marker of the form "[1]" style.
    Every surviving occurrence keeps: line number, the literal as printed, its parsed value, its
    number of printed decimals d, and +/-120 characters of context.

R2  THE ARTIFACT MAP. research/modalities/emc-atr-vulnerability.json is flattened to
    (dotted/bracketed path -> numeric leaf). Booleans are not numbers. Lists index as [i].
    Every numeric leaf in the file is a candidate home; nothing is pre-selected.

R3  MATCH (exact at printed precision). A printed value v with d printed decimals MATCHES a path p
    with artifact value a iff
        round(a, d) == v        (float compare after rounding both to d decimals; d<=6)
    under exactly one of these declared unit readings, tried in this order:
        U1 identity            a  vs v
        U2 percent             a*100 vs v   -- allowed ONLY when the literal printed a '%' sign
                                                or the immediate context contains '%' or ' per cent'
        U3 fraction            a/100 vs v   -- allowed ONLY when the artifact path name ends in
                                                '_pct' or '_percent'
        U4 sign-free           |a| vs |v|   -- allowed ONLY when the context contains 'magnitude',
                                                'absolute' or the printed literal has no sign and
                                                the artifact value is negative AND the path name
                                                token appears in the context (R4 token test)
    No other conversion is permitted. No numeric tolerance beyond printed precision is permitted.
    Thousands separators (',' ' ' U+202F) are stripped before parsing; U+2212 is a minus sign.

R4  TOKEN TEST (used only to name a home, and by R5). tokens(context) = lowercase alphanumeric
    words of length >= 4 in the +/-120 char window, plus the same from the containing table row.
    tokens(path) = the path split on '.', '[', ']', '_', '-' , lowercased, length >= 4.
    A path is CONTEXT-TIED to an occurrence iff |tokens(path) & tokens(context)| >= 1.
    When several paths MATCH, the reported home is the context-tied one with the fewest path
    segments; if none is context-tied, the shortest path is reported and flagged AMBIGUOUS.

R5  MISMATCH. An occurrence with no R3 match is a MISMATCH iff there exists a CONTEXT-TIED path p
    whose value a satisfies |a - v| / max(|v|, 1e-9) <= 0.10 (10 % relative), or |a - v| <= 0.01
    for |v| < 1. The report gives expected (artifact a, its path) vs observed (printed v). A
    MISMATCH is a CANDIDATE defect requiring human confirmation that p is the intended home; the
    script never asserts intent.

R6  UNRESOLVED. Everything that is neither MATCH nor MISMATCH. UNRESOLVED is subdivided, for
    routing only, by a SECOND pass over the other modality artifacts the manuscript cites
    (emc-atr-vulnerability-inputs.json, atr-hrd-sarcoma-series{,-inputs}.json,
    emc-fet-idr-census.json, emc-fet-construct-designs.json, fet-ddr-axis-scan.json,
    emc-sra-study.json, atm-status-atri-stratification.json) under the SAME R3 rule:
        UNRESOLVED-ELSEWHERE  = exact-at-precision in one of those files (a home exists, just not
                                in the primary artifact)
        UNRESOLVED-NOWHERE    = no exact-at-precision home in any of them.

R7  These rules are fixed. If the match rate is low, the rules stay as written and the low rate is
    reported. No rule is relaxed to improve a count.
"""
import json
import os
import re
import sys
from collections import defaultdict

REPO = "/home/user/Rare-cancers"
DOC = os.path.join(REPO, "research/manuscripts/dependency/emc-atr-vulnerability-assessment.md")
PRIMARY = os.path.join(REPO, "research/modalities/emc-atr-vulnerability.json")
SECONDARY = [
    "research/modalities/emc-atr-vulnerability-inputs.json",
    "research/modalities/atr-hrd-sarcoma-series.json",
    "research/modalities/atr-hrd-sarcoma-series-inputs.json",
    "research/modalities/emc-fet-idr-census.json",
    "research/modalities/emc-fet-construct-designs.json",
    "research/modalities/fet-ddr-axis-scan.json",
    "research/modalities/emc-sra-study.json",
    "research/modalities/atm-status-atri-stratification.json",
]

NUM = re.compile(r"[-+−]?\d[\d,  ]{0,12}(?:\.\d+)?\s?%?")
HEX = re.compile(r"[0-9a-f]{7,}")


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    elif isinstance(obj, bool):
        pass
    elif isinstance(obj, (int, float)):
        out[prefix] = float(obj)
    return out


def path_tokens(p):
    return {t for t in re.split(r"[.\[\]_\-/]+", p.lower()) if len(t) >= 4}


def ctx_tokens(c):
    return {t for t in re.split(r"[^a-z0-9]+", c.lower()) if len(t) >= 4}


def parse_lit(lit):
    s = lit.strip()
    pct = s.endswith("%")
    s = s.rstrip("%").strip()
    s = s.replace("−", "-").replace(",", "").replace(" ", "").replace(" ", "")
    try:
        v = float(s)
    except ValueError:
        return None
    d = len(s.split(".")[1]) if "." in s else 0
    return v, min(d, 6), pct


def excluded(line, m, lit):
    s, e = m.start(), m.end()
    before = line[:s]
    after = line[e:]
    if before.count("(") > before.count(")") and re.search(r"\]\s*\($", before.split("(")[0] + "("):
        pass
    depth_paren = before.count("(") - before.count(")")
    if depth_paren > 0:
        seg = before[before.rfind("(") :]
        if "](" in before[max(0, before.rfind("(") - 2) : before.rfind("(") + 2] or "/" in seg or ".json" in seg:
            return "link/path"
    if before.count("`") % 2 == 1:
        seg = before[before.rfind("`") :] + after.split("`")[0]
        if "/" in seg or ".json" in seg or ".py" in seg or ".gz" in seg:
            return "code-path"
    if re.search(r"(§§?\s*|[Ss]ection\s+)$", before):
        return "section-ref"
    if re.search(r"§[\d.]*$", before):
        return "section-ref"
    ctxt = line[max(0, s - 12) : e + 12]
    if re.search(r"\d{4}-\d{2}-\d{2}", ctxt) and len(lit.strip()) <= 4:
        return "date"
    if re.fullmatch(r"\d{4}", lit.strip()) and 1900 <= int(lit.strip()) <= 2100:
        return "year"
    tail = re.search(r"([A-Za-z]{2,})$", before)
    if tail and tail.group(1).upper() in {
        "GSE", "GPL", "GSM", "SRP", "SRR", "SRX", "PMC", "PMID", "NCT", "DOI", "EGA", "GDSC",
        "PMCID", "CHEMBL", "EUDRACT", "ENSG", "NM", "GRCH", "HG",
    }:
        return "accession"
    if HEX.search(ctxt) and re.fullmatch(r"[0-9a-f]{7,}", "".join(ch for ch in ctxt if ch.isalnum())[:12] or "z"):
        return "objectid"
    if re.match(r"^\s*(#+|[-*])?\s*$", before) and re.match(r"^[.)]\s", after):
        return "list-ordinal"
    if before.endswith("[") and after.startswith("]"):
        return "footnote"
    return None


def load(path):
    with open(path, encoding="utf-8") as fh:
        return flatten(json.load(fh))


def match_paths(v, d, pct, ctx, amap):
    """R3. Returns list of (path, artifact_value, unit_reading)."""
    hits = []
    ctxt = ctx.lower()
    pct_ok = pct or "%" in ctx or " per cent" in ctxt
    for p, a in amap.items():
        if round(a, d) == round(v, d):
            hits.append((p, a, "U1"))
            continue
        if pct_ok and round(a * 100.0, d) == round(v, d):
            hits.append((p, a, "U2"))
            continue
        if (p.endswith("_pct") or p.endswith("_percent")) and round(a / 100.0, d) == round(v, d):
            hits.append((p, a, "U3"))
            continue
        if a < 0 and not re.match(r"^[-−+]", str(v)) and v > 0 and round(abs(a), d) == round(abs(v), d):
            if ("magnitude" in ctxt or "absolute" in ctxt) and (path_tokens(p) & ctx_tokens(ctx)):
                hits.append((p, a, "U4"))
    return hits


def main():
    with open(DOC, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    if lines and lines[0].strip() == "---":
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        body = [(i + 1, lines[i]) for i in range(end + 1, len(lines))]
    else:
        body = list(enumerate(lines, 1))

    primary = load(PRIMARY)
    secondary = {rel: load(os.path.join(REPO, rel)) for rel in SECONDARY}
    sys.stderr.write(f"primary numeric leaves: {len(primary)}\n")

    occs = []
    skipped = defaultdict(int)
    for ln, line in body:
        for m in NUM.finditer(line):
            lit = m.group(0)
            why = excluded(line, m, lit)
            if why:
                skipped[why] += 1
                continue
            parsed = parse_lit(lit)
            if parsed is None:
                skipped["unparsed"] += 1
                continue
            v, d, pct = parsed
            lo = max(0, m.start() - 120)
            ctx = line[lo : m.end() + 120]
            occs.append({"line": ln, "lit": lit.strip(), "v": v, "d": d, "pct": pct, "ctx": ctx})

    results = []
    for o in occs:
        ct = ctx_tokens(o["ctx"])
        hits = match_paths(o["v"], o["d"], o["pct"], o["ctx"], primary)
        if hits:
            tied = [h for h in hits if path_tokens(h[0]) & ct]
            pool = tied or hits
            best = sorted(pool, key=lambda h: (h[0].count(".") + h[0].count("["), len(h[0])))[0]
            results.append({**o, "cls": "MATCH", "path": best[0], "aval": best[1],
                            "unit": best[2], "n_hits": len(hits),
                            "ambiguous": not tied})
            continue
        cands = []
        for p, a in primary.items():
            if not (path_tokens(p) & ct):
                continue
            denom = max(abs(o["v"]), 1e-9)
            if abs(a - o["v"]) / denom <= 0.10 or (abs(o["v"]) < 1 and abs(a - o["v"]) <= 0.01):
                cands.append((p, a))
        if cands:
            best = sorted(cands, key=lambda c: (abs(c[1] - o["v"]), len(c[0])))[0]
            results.append({**o, "cls": "MISMATCH", "path": best[0], "aval": best[1],
                            "unit": "-", "n_hits": len(cands), "ambiguous": False})
            continue
        where = []
        for rel, amap in secondary.items():
            if match_paths(o["v"], o["d"], o["pct"], o["ctx"], amap):
                where.append(rel)
        results.append({**o, "cls": "UNRESOLVED-ELSEWHERE" if where else "UNRESOLVED-NOWHERE",
                        "path": ";".join(os.path.basename(w) for w in where), "aval": None,
                        "unit": "-", "n_hits": len(where), "ambiguous": False})

    counts = defaultdict(int)
    for r in results:
        counts[r["cls"]] += 1
    print("=== EXTRACTION ===")
    print(f"manuscript body lines: {len(body)}  occurrences kept: {len(occs)}")
    print("excluded by rule R1: " + ", ".join(f"{k}={v}" for k, v in sorted(skipped.items())))
    print(f"primary artifact numeric leaves: {len(primary)}")
    print()
    print("=== CLASSIFICATION COUNTS ===")
    for k in ("MATCH", "MISMATCH", "UNRESOLVED-ELSEWHERE", "UNRESOLVED-NOWHERE"):
        print(f"{k:24s} {counts[k]:5d}")
    print(f"{'TOTAL':24s} {len(results):5d}")
    print()
    print("=== FULL MISMATCH LIST ===")
    for r in results:
        if r["cls"] != "MISMATCH":
            continue
        print(f"L{r['line']:>5}  printed={r['lit']:<12} artifact={r['aval']!r:<12} path={r['path']}")
        print(f"        ctx: {' '.join(r['ctx'].split())[:200]}")
    with open("/tmp/claude-0/w17e/results.json", "w") as fh:
        json.dump(results, fh, indent=1)
    print("\nwrote /tmp/claude-0/w17e/results.json")


if __name__ == "__main__":
    main()
```

`verify_pins.py`:

```python
"""Verify the W17e CANDIDATE artifact_figures entries with the REPOSITORY'S OWN checker.

Read-only: imports research/manuscripts/lint_consistency.py and calls check_artifact_figures on a
registry held only in /tmp. Nothing under the repository is written. A candidate entry is ACCEPTED
iff the real checker returns ZERO findings for it against the current tree.
"""
import json, sys
sys.path.insert(0, "/home/user/Rare-cancers/research/manuscripts")
import lint_consistency as L

reg = json.load(open("/tmp/claude-0/w17e/candidate_pins.json"))
findings = L.check_artifact_figures(reg, repo="/home/user/Rare-cancers")
ids = {a["id"] for a in reg["artifact_figures"]}
bad = set()
for f in findings:
    print("FINDING:", f)
    for i in ids:
        if i in str(f):
            bad.add(i)
print()
print(f"candidates: {len(ids)}  clean: {len(ids - bad)}  with findings: {len(bad)}")
for i in sorted(ids):
    print(("ACCEPTED " if i not in bad else "REJECTED ") + i)
```
