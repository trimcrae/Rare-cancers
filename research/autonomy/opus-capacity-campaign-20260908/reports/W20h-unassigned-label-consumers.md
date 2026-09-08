<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:18:29Z UTC
     agent id a17fce3037e458e1e ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a17fce3037e458e1e.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

**W20h** · lane 20 refill · OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:11:26 UTC 2026` | `Tue Sep  8 03:14:07 UTC 2026` |
| `git rev-parse HEAD` | `98a0833f1ede2cf9cef13790388260567a32e868` | `98a0833f1ede2cf9cef13790388260567a32e868` (**unchanged**) |
| `git status --porcelain` | 8 untracked worker reports (W01g, W02f, W04e, W06f, W07f, W09f, W12e, W20g) | **byte-identical, same 8 lines** |

HEAD did not move under me. Every file I measured re-hashed identically at the end: `emc-fourth-cohort-probe-counts.tsv` `c689e0fd…d26fc`, `emc-fourth-cohort-gene-counts.tsv` `8aa3064a…180cc`, `emc-fourth-cohort-quant.json` `1769b3f0…c5165`, `emc-fourth-cohort-route-readout.json` `d4e00635…8890`, `emc-fourth-cohort-quant-inputs.json` `bdb38ded…4bbf`. **I wrote nothing into the tree and ran no git write.** All execution under `/tmp/claude-0/w20h/`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (the four long proxy lines — `no_proxy`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are retained verbatim in the transcript, carry no model information, and are elided here as `…`):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=… (proxy list, no model information)
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
GLOBAL_AGENT_NO_PROXY=… (proxy list, no model information)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=… (truststore + proxy, no model information)
NO_PROXY=… (proxy list, no model information)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=… (proxy list, no model information)
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

**Stop when all five are answered from committed bytes with no network: (1) W20g's 662 / 77 / 211,362 decomposition and its 0-disagreement TSV cross-check independently reproduced or corrected with my own script; (2) every gene the readout scores enumerated with its `file:line` and its membership in the 862; (3) every downstream sentence in `emc-fourth-cohort-route-readout.json`, `systems/graph/routes.json` and `systems/views/` that rests on a `false` row located by `file:line` and graded survives / fails / UNKNOWN; (4) for each scored gene, whether a sequence bearing its assignment could even have been offered, answered from committed data or declared UNKNOWN-offline; (5) W20g's `probe_counts_sha256` drift-key finding confirmed or corrected.** — **MET, all five.** Returning immediately.

---

## Question

**Which published conclusions rest on a `false` row or an absent gene in `emc-fourth-cohort-route-readout.json`, and does each survive the missing third branch W20g found?**

Open because W20g established the defect (one string `unassigned`, three disjoint populations; the readout offers a two-branch disjunction) but explicitly stopped at flagging one route. Nobody had enumerated what actually depends on those rows. This is the difference between "an artifact has a labelling defect" and "N published verdicts are affected, of which k are refuted, m are UNKNOWN and the rest are unharmed" — and it needs no network, because the readout, the routes graph and the generated views are all committed.

---

## Prior-work check

| Command | What it showed |
|---|---|
| Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W20g-published-denominator-consistency.md`; `reports/W20f-probe-intersection-filter.md` §Question–§6; `reports/W20d-probe-power-audit.md` §Question–§Prior-work; `reports/W20e` via W20f's transcription | W20g's §3 is the given. Its "Next concrete action" names a *code repair* I did not author; my task is the orthogonal downstream trace. |
| `grep -rn "probe_to_several_genes\|probe_to_gene" --include=*.py --include=*.json --include=*.md .` | **19 hits. The decisive one is new: `research/modalities/emc-fourth-cohort-quant-inputs.json:1656` carries the full `probe_to_several_genes` map, committed.** W20g reported it "dropped from the published JSON at `:801` and never reaching the TSV" — true of `emc-fourth-cohort-quant.json`, but the map survives in the inputs cache, which makes the multi-gene branch **testable offline**. This is a correction-by-extension to W20g, not a contradiction. |
| `grep -rn "assigned probe\|1,645\|fourth cohort" systems/views/` and the same over `systems/graph/routes.json` | 13 view sentences and 13 routes sentences located, one per adjudicated route. |
| `grep -n "in_fourth_cohort" research/modalities/emc-fourth-cohort-route-readout.json` (parsed) | 67 gene rows across 14 routes; 59 distinct genes. |

**Confirmed not replayed.** I did **not** re-run W20e's closed EWSR1 endpoint; I computed **no** δ, p-value or panel percentile; I authored **no** filter repair; I did **not** reopen, re-grade or unblock `AUT-PD-116` or `RT-IMMUNOCYTOKINE`; I edited nothing under `systems/graph/`. **I did not run `emc_fourth_cohort_quant.py --check`** — I re-verified W20g's reason by reading the source: `main()` calls `derive()` unconditionally before the `--check` comparison, and `derive()` writes both TSVs. **No network request of any kind**: the Ensembl fetch and the vendor TempO-Seq manifest remain honest unrecovered sources and were not attempted, probed or routed around. No content-policy refusal was encountered.

---

## Method / inputs

| Input | Path | sha256 (measured, start = end) | Use |
|---|---|---|---|
| The readout under trace | `/home/user/Rare-cancers/research/modalities/emc-fourth-cohort-route-readout.json` (734 lines) | `d4e00635f8a3aee6c0e7af661d379b44c19c3963306ee498b392114e847b8890` | every `false` row, every gloss |
| Probe × run table | `.../emc-fourth-cohort-probe-counts.tsv` | `c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc` | 213,007 × 12; re-verification |
| Gene × run table | `.../emc-fourth-cohort-gene-counts.tsv` | `8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc` | 862 × 12; cross-check |
| Published counts | `.../emc-fourth-cohort-quant.json` | `1769b3f0ee01f1a640dabc6c4f36ce86630ff62f87249400e070a4638fcf5165` | the denominators |
| **Matcher's multi-gene map** | `.../emc-fourth-cohort-quant-inputs.json` → `probe_map.probe_to_several_genes` (`:1656`) | `bdb38dedeafda696fe87f88846baf370c4911ffeed7a65dd5d0872be26f24bbf` | **tests the second branch offline** |
| Committed transcript models | `.../emc-construct-inputs.json` → `genes.{EWSR1,TAF15,FUS,TCF12,TFG,NR4A3,PGR}.{cdna,cds}` | — | offline 50-mer membership; **only 7 genes on disk** |
| Downstream prose | `systems/graph/routes.json`, `systems/views/L2-rt-*.md` | — | `file:line` of every dependent sentence |

**Tools:** Python 3.11 stdlib only (`json`, `hashlib`, `collections`, `re`). No third-party package, no network, no GPU, no paid API. Scripts at `/tmp/claude-0/w20h/{recheck.py, …}`.

**Operational definition, load-bearing:** "present in run *r*" = a **non-zero** cell, which is the code's own definition (`_read_probe_tsv` inserts a key only `if n:`). **A zero cell means the sequence was not among the counts PERSISTED for that run — missing data, never a measured zero and never a statement about the tumour.** Every count below counts persistence.

---

## Result

### 1. W20g's decomposition, independently re-derived — I agree exactly, no disagreement to report

`PRIMARY`, RUN, exit 0, from the committed bytes with a script written without reference to W20g's.

| Quantity | W20g | **W20h (independent)** | Verdict |
|---|---|---|---|
| Probe TSV rows | 213,007 | **213,007** | agree |
| Rows labelled `unassigned` | 212,101 | **212,101** | agree |
| Rows carrying a gene | 906 | **906** | agree |
| k = 12 (offered) | 1,645 | **1,645** | agree |
| **Offered and unmatched** | **662** | **662** | agree |
| **Offered and multi-gene** | **77** | **77** | agree |
| **Never offered** | **211,362** | **211,362** | agree |
| Sum check | 212,101 | 662 + 77 + 211,362 = **212,101** | agree |
| Identity `offered = unique + multi + unassigned` | 1,645 | 906 + 77 + 662 = **1,645** | agree |
| Distinct genes in probe TSV | 862 | **862**, and the set is **identical** to the gene TSV's | agree |
| Gene-TSV cells vs per-gene sums over the probe TSV | 0 disagreements | **0 of 10,344 cells disagree** | agree |
| `per_run.*.n_sequences_persisted` | 0 mismatches | **0 of 12 mismatch** | agree |
| k histogram | W20f's table | reproduced identically, `{1:162981, 2:17404, 3:8246, 4:4103, 5:4051, 6:2668, 7:2644, 8:2561, 9:2493, 10:2217, 11:1994, 12:1645}` | agree |

**Nothing to correct. W20g's numbers stand, now on two independent recomputations.** One incidental defect my script surfaced (`PRIMARY`, minor): **the two committed TSVs label their run columns differently** — the probe TSV header reads `SRR35940646:SRR35940646 …` while the gene TSV reads `SRR35940646:Si19 …`. The SRR order is identical, so no count is affected, but a consumer joining the two files on column name gets zero matches.

### 2. The second branch is testable offline, and it is **excluded for every scored gene**

`PRIMARY`, RUN, exit 0. This is the substantive extension to W20g. `probe_to_several_genes` **is committed** at `research/modalities/emc-fourth-cohort-quant-inputs.json:1656` — 77 probes, resolving to **149 distinct gene symbols**.

- **None of the 59 genes the readout scores appears among those 149.** The intersection is empty. So for all 50 `false` rows, the "matched-but-labelled-unassigned" population W20g identified is **ruled out as the cause** — no scored gene's `false` cell is contradicted by the matcher's own multi-gene output.
- Independently: `probe_to_gene` has 906 entries over **862** distinct symbols, and that symbol set is **exactly** the 862 in both TSVs (`==` True). The readout's 59 rows agree with the 862 set with **zero disagreements** — every `true` gene is in it, every `false` gene is not.
- Side finding, `PRIMARY`: **136 of the 149 multi-gene symbols are absent from the 862** (13 overlap). These are gene symbols the matcher actually hit that appear in **no** published table — a second, smaller invisible population. None is a scored gene, so nothing downstream turns on it here.

**Consequence for the trace:** each `false` row now has exactly **two** possible explanations rather than three — *offered and unmatched* (one of the 662) or *never offered* (one of the 211,362). Distinguishing those requires running the matcher, which requires the denied Ensembl fetch. **UNKNOWN offline for every gene except the three with committed cDNA (§4).**

### 3. Every gene the readout scores, with `file:line` and verdict

`file:line` = `research/modalities/emc-fourth-cohort-route-readout.json`. 67 rows, 59 distinct genes, 14 routes. `PRIMARY` for membership.

**The 9 `true` rows** — each verified present in the 862 and its probe count recomputed:

| Gene | line | route(s) | n assigned probes (recomputed) |
|---|---|---|---|
| BGN | 123, 523 | RT-CART-SURFACE, RT-MATRIX-SYNTHESIS | 1 |
| CD44 | 130 | RT-CART-SURFACE | 1 |
| VCAN | 144, 516 | RT-CART-SURFACE, RT-MATRIX-SYNTHESIS | 1 |
| TAF15 | 289 | RT-FUSION-OUTPUT | 1 |
| CHSY1 | 446 | RT-MATRIX-SYNTHESIS | 1 |
| CSGALNACT2 | 467 | RT-MATRIX-SYNTHESIS | 1 |
| CSPG4 | 541 | RT-MATRIX-ADDRESS | 1 |
| **FN1** | **572** | RT-IMMUNOCYTOKINE | **1** |
| VEGFA | 609 | RT-HYPOXIA-PRODRUG | 1 |

**All 50 `false` rows**, grouped by route, with line numbers: SSTR2 (74) · CD276 (90), NCAM1 (96) · ALCAM (116), GPC1 (137) · FAP (160) · CTAG1B (181), MAGEA3 (185), SSX2 (189), CTAG2 (193), MAGEA4 (199), PRAME (206) · HLA-A (227, 672), HLA-B (234, 679), HLA-C (240, 685), B2M (247), TAP1 (254), TAP2 (261) · **EWSR1 (282)**, **NR4A3 (296, 379)**, ENO3 (303), PPARG (310), SEMA3C (317) · MTAP (336), PRMT5 (343), MAT2A (350), CDKN2A (357) · CDK7 (398), CDK9 (405), CDK12 (412), CDK13 (419) · CHPF (453), CSGALNACT1 (460), CHST11 (474, 548), CHST3 (481, 555), UST (488), PAPSS1 (495), PAPSS2 (502), ACAN (509) · **TNC (579)** · CA9 (602), SLC2A1 (616), LDHA (623), HIF1A (630), EGLN3 (637), ADM (644), P4HA1 (651) · CD274 (692), PDCD1 (699), CTLA4 (705).

**The narrow factual content of every one of those 50 cells — "this gene has no probe in `probe_to_gene`, so no row in the committed gene table" — SURVIVES.** Verified against the 862 set with zero disagreements, and now also against `probe_to_several_genes` with zero hits. **What does not survive is the published gloss of what the cell means**, at line 14.

### 4. Could a sequence bearing that gene's assignment have been offered? Answerable for 3 of 59

The dispatch's central question. Committed transcript models exist for exactly **seven** genes (`emc-construct-inputs.json`), of which **three** are scored in the readout: EWSR1, TAF15, NR4A3. For the other 56 there is no committed sequence to test against, and the matcher's own input is behind the denied Ensembl fetch — **UNKNOWN, and I stop there.**

`PRIMARY` for presence, `k` and label; **`UNVERIFIED` for probe identity** (nothing on disk says these 50-mers are TempO-Seq probes — the vendor manifest is absent). Method: every 50-mer of the committed `cdna` and `cds`, both strands, tested for exact membership in the 213,007-sequence key set. Independently re-derived; it reproduces W20f exactly.

| Gene | readout row | candidate 50-mer in the table? | locus | label | **k** | offered? |
|---|---|---|---|---|---|---|
| **TAF15** | 289 `true` | yes, 1 | cDNA 1617–1666, antisense | `TAF15` | **12** | **yes** — control, behaves as published |
| **EWSR1** | 282 `false` | **yes, 1** | cDNA 453–502, antisense | `unassigned` | **10** | **NO — never offered** (counts `337, 521, 423, 459, 807, 0, 0, 735, 791, 999, 281, 183`) |
| **NR4A3** | 296 + 379 `false` | **yes, 1** | cDNA 882–931, antisense | `unassigned` | **9** | **NO — never offered** (counts `65, 141, 0, 144, 87, 0, 209, 161, 108, 396, 0, 417`) |

**For EWSR1 and NR4A3 the readout's two-branch disjunction at line 14 is FALSIFIED from committed bytes alone.** A 50-nt sequence exactly matching the committed cDNA of each gene **is in the table**, persisting in 10 and 9 of 12 runs respectively, and was excluded by the intersection filter before the matcher ran. Neither "on the panel and unmatched" nor "off it" describes that state. The two zeros in EWSR1's row and the three in NR4A3's are **missing data, not measured zeros** — that is precisely why the intersection dropped them. Whether the matcher *would* have assigned those sequences is a **PREDICTION, not a measurement**: it needs the matcher and therefore the denied Ensembl fetch. **UNKNOWN, and I stop there.**

For the remaining 48 `false` genes: **UNKNOWN offline.** Each is either one of the 662 offered-and-unmatched or one of the 211,362 never-offered; §2 rules out the third possibility, and nothing further is derivable without the fetch.

### 5. The downstream trace — every dependent sentence, with `file:line` and verdict

`PRIMARY` for location and for the survives/fails grading of each sentence's *stated* content.

**The gloss every `false` row inherits.**

> `research/modalities/emc-fourth-cohort-route-readout.json:14` — `⛔ _what_a_false_row_is_not`: *"…The gene may be on the panel and unmatched, or off it."*

**FAILS as published.** Demonstrated false for EWSR1 (line 282) and NR4A3 (lines 296, 379) by §4; **UNKNOWN** for the other 48, which are covered by a disjunction now known to be non-exhaustive. This one sentence is inherited by all 50 rows and is the single load-bearing defect.

**Route-level sentences.** Each route's adjudication in `systems/graph/routes.json` is transcribed verbatim into one `systems/views/L2-rt-*.md` row, so both carry the same verdict.

| Route | `systems/graph/routes.json` | `systems/views/` | The claim as published | **Verdict** |
|---|---|---|---|---|
| RT-SSTR2 | `:2068` | `L2-rt-sstr2.md:76` | "SSTR2 has no assigned probe in the fourth cohort." | **survives** (narrow, true of the gene table) |
| RT-B7H3 | `:2216` | `L2-rt-b7h3.md:71` | "CD276 and NCAM1 have no assigned probe in the fourth cohort." | **survives** |
| RT-CART-SURFACE | `:2342` | `L2-rt-cart-surface.md:71` | "…adds BGN, CD44 and VCAN in twelve more tumours and **no ALCAM or GPC1 probe**." | **survives** narrowly; "no probe" reads as a panel statement — **UNKNOWN** whether ALCAM/GPC1 sequences sit among the 211,362 |
| RT-JUNCTION-NEOANTIGEN | `:2587` | `L2-rt-junction-neoantigen.md:65` | "None of HLA-A, HLA-B, HLA-C, B2M, TAP1 or TAP2 has an assigned probe…" | **survives** |
| RT-TCRT-CTA | `:3110`, `:3134` | `L2-rt-tcrt-cta.md:69`, `:138` | "none of the three has an assigned probe in the fourth cohort's committed gene table"; **"That is an instrument state on three instruments and NEVER a negative about the tumour"** | **survives, and this is the best-scoped sentence in the set** — it names "the committed gene table" as its denominator and refuses the tumour reading unprompted |
| RT-FAP-RLT | `:3448` | `L2-rt-fap-rlt.md:75` | "FAP has no assigned probe in the fourth cohort." | **survives** |
| **RT-SYNPROMOTER** | `:4744` | `L2-rt-synpromoter.md:66` | **"NR4A3 has no assigned probe in the fourth cohort."** | narrow claim **survives**; as a statement about the panel it is **misleading** — §4 shows an exact NR4A3 cDNA 50-mer in the table at k = 9, never offered |
| **RT-FUSION-OUTPUT** | `:5405` | `L2-rt-fusion-output.md:59` | **"TAF15 has an assigned probe in that cohort; EWSR1 and NR4A3 do not."** | narrow claim **survives**; the panel reading is **falsified** for both EWSR1 (k = 10) and NR4A3 (k = 9) |
| RT-TXN-CDK | `:5681` | `L2-rt-txn-cdk.md:68` | "No CDK7, CDK9, CDK12 or CDK13 probe in the fourth cohort." | **survives** narrowly; panel reading **UNKNOWN** |
| RT-MTAP-PRMT5 | `:5888` | `L2-rt-mtap-prmt5.md:66` | "The fourth cohort adds nothing — no MTAP, PRMT5, MAT2A or CDKN2A probe, **and it would be expression either way**." | **survives** — the conclusion is carried by the copy-number-versus-transcript argument, which is independent of the probe rows |
| RT-MATRIX-SYNTHESIS | `:7049` | `L2-rt-matrix-synthesis.md:64` | "…and no CHST11, CHST3 or PAPSS probe." | **survives** narrowly; panel reading **UNKNOWN** |
| RT-MATRIX-ADDRESS | `:7142` | `L2-rt-matrix-address.md:71` | "CSPG4 has an assigned probe and CHST11 and CHST3 … do not." | **survives** narrowly; panel reading **UNKNOWN** |
| **RT-IMMUNOCYTOKINE** | `:7235`, `:7258` | `L2-rt-immunocytokine.md:69`, `:123` | see below | **mixed — see below** |
| RT-HYPOXIA-PRODRUG | `:7328` | `L2-rt-hypoxia-prodrug.md:65` | "Of the hypoxia genes only VEGFA has an assigned probe…; CA9, SLC2A1, LDHA, HIF1A, EGLN3, ADM and P4HA1 do not." | **survives** narrowly; panel reading **UNKNOWN** |
| RT-VACCINE-COMBINATION | `:8845`, `:8852` | — | **no per-gene absence claim is made** | **unaffected** — its 6 `false` rows carry nothing downstream |

**RT-IMMUNOCYTOKINE, the route the dispatch named, taken leg by leg.** The published verdict is `routes.json:7235` / `L2-rt-immunocytokine.md:69` — *"THE ANSWER IS NO: the fourth cohort cannot resolve the oncofetal fibronectin and tenascin domains"* — restated at `routes.json:7258` / `L2-rt-immunocytokine.md:123`, and sourced from `route-readout.json:725–731`.

| Leg | as published | verdict |
|---|---|---|
| *"TNC has no assigned probe at all, so the tenascin parent gene is not readable in this cohort at all"* (`readout:727`, `routes.json:7235`) | first clause narrow, second clause a panel claim | first clause **survives** (TNC confirmed absent from the 862); **"not readable in this cohort at all" is UNKNOWN** — whether a TNC-bearing sequence sits among the 211,362 needs the matcher and the denied Ensembl fetch, and TNC has no committed cDNA to test offline |
| *"FN1 has exactly one assigned probe **across the 1,645 probes common to every run**"* (`readout:728`) | correctly scoped — names its denominator inline | **survives.** One qualification worth recording, `PRIMARY`: **823 of the 862 genes have exactly one probe** (distribution `{1: 823, 2: 36, 3: 2, 5: 1}`), so "exactly one" is the modal case, not a scarcity specific to FN1. It does not weaken the isoform argument, which does not depend on probe count |
| *"the committed probe table carries `probe_sequence` and `assigned_gene` and no transcript or exon identity, so no domain-inclusion call is derivable from it"* (`readout:729`) | structural | **survives, and it is sufficient on its own.** I verified the header is exactly `probe_sequence⇥assigned_gene⇥<12 run columns>`. This leg is untouched by the missing branch |
| **The verdict "NO"** | conjunction of the three | **SURVIVES — on the third leg alone.** A gene-level count table with no exon identity cannot make a domain-inclusion call regardless of how many probes any gene has. The route's `⛔ therefore` and its "still needs transcript-resolved sequencing, or the vendor probe manifest" also stand |

**So the headline for the route named in the dispatch is: the conclusion holds, but not for the first reason it gives.** One of its three supporting legs (TNC "not readable at all") is UNKNOWN offline rather than established, and the verdict does not depend on it. **This is not a reopening, a re-grade or an unblock of `AUT-PD-116` or `RT-IMMUNOCYTOKINE`** — no route state, grade or blocker is touched, and I edited nothing under `systems/graph/`.

**Summary of the trace.** 50 `false` rows → 13 route sentences in `routes.json`, each mirrored in one `systems/views/L2-rt-*.md` row (26 sentences), plus 2 readout answers and 1 inherited gloss. **Zero published verdicts are refuted. One inherited gloss (`readout:14`) fails. Two route sentences (RT-FUSION-OUTPUT `:5405`, RT-SYNPROMOTER `:4744`) are narrowly true but carry a panel implication falsified for EWSR1 and NR4A3. Nine route sentences are narrowly true with an UNKNOWN panel implication. Two (RT-TCRT-CTA, RT-MTAP-PRMT5) are unaffected because their wording already names the right denominator or rests on an independent argument. One route (RT-VACCINE-COMBINATION) carries nothing downstream at all.**

### 6. W20g's drift-key finding — **CONFIRMED, verbatim**

`PRIMARY`, from `research/modalities/emc_fourth_cohort_quant.py`, the `--check` branch:

```python
drift = [k for k in ("probe_gate", "n_runs_read", "n_probes_common_to_every_read_run",
                     "n_genes_with_at_least_one_assigned_probe", "gene_counts_sha256")
         if old.get(k) != out.get(k)]
```

`gene_counts_sha256` is present; **`probe_counts_sha256` is absent**, though the artifact publishes it (`c689e0fd…d26fc`, verified). W20g is correct: the 213,007-row table can change without `--check` reporting drift, while the 862-row table cannot. I also confirmed W20g's reason for not running `--check`: `derive()` is called before the comparison and writes both TSVs into the tree.

---

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24 x86_64, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Python 3.11 stdlib only, no network, cwd `/tmp/claude-0/w20h`.

```
$ python3 /tmp/claude-0/w20h/recheck.py ; echo EXIT=$?
probe_tsv_sha256 c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc
gene_tsv_sha256  8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc
header ['probe_sequence', 'assigned_gene'] n_run_cols 12
n_probe_rows 213007
labelled 906 unassigned 212101
distinct genes in probe TSV 862
k=12 offered 1645
json n_probes_offered 1645 n_probes_assigned_to_one_gene 906 multi 77 unassigned 662
identity offered==u+m+un: 1645 == 1645
DECOMPOSITION offered_unmatched 662 offered_multigene 77 never_offered 211362 total 212101 == 212101
k histogram {1: 162981, 2: 17404, 3: 8246, 4: 4103, 5: 4051, 6: 2668, 7: 2644,
             8: 2561, 9: 2493, 10: 2217, 11: 1994, 12: 1645}
k hist of labelled rows {12: 906}
gene tsv header0 gene cols 12 rows 862
probe hdr run labels ['SRR35940646:SRR35940646', ...] || gene hdr run labels ['SRR35940646:Si19', ...]
gene tsv cells 10344 disagreeing 0
gene sets identical True n 862
per-run persisted mismatches 0 of 12
published probe_counts_n_rows 213007 gene_counts_n_rows 862
EXIT=0
```

```
$ python3  # multi-gene map + scored-gene cross-check ; EXIT=0
PATH /probe_map/probe_to_several_genes n_entries 77
PATH /probe_map/probe_to_gene n_entries 906
distinct symbols across multi-gene probes: 149
distinct genes scored: 59
true rows: ['BGN','CD44','CHSY1','CSGALNACT2','CSPG4','FN1','TAF15','VCAN','VEGFA']
false rows n= 50
readout-vs-862 disagreements: []
SCORED GENES APPEARING IN probe_to_several_genes: {}
n unique-map symbols 862 == 862? True   set equal to TSV genes: True
multi symbols also in the 862: 13 ; multi symbols NOT in the 862: 136
```

```
$ python3  # 50-mer membership, both strands, cdna+cds ; EXIT=0
probe sequence length (uniform?): {50}
== EWSR1 distinct candidate sequences: 1
    cdna pos 453 antisense label= unassigned k= 10 counts= [337,521,423,459,807,0,0,735,791,999,281,183]
== NR4A3 distinct candidate sequences: 1
    cdna pos 882 antisense label= unassigned k= 9  counts= [65,141,0,144,87,0,209,161,108,396,0,417]
== TAF15 distinct candidate sequences: 1
    cdna pos 1617 antisense label= TAF15 k= 12 counts= [1298,3585,1489,1563,2603,276,204,785,701,3028,783,429]
```

```
$ python3  # per-gene probe counts ; EXIT=0
BGN 1 · CD44 1 · CHSY1 1 · CSGALNACT2 1 · CSPG4 1 · FN1 1 · TAF15 1 · VCAN 1 · VEGFA 1
TNC in table? False
probes-per-gene distribution: {1: 823, 2: 36, 3: 2, 5: 1}   n genes with >1 probe: 39
```

```
$ git status --porcelain      # start and end — identical, 8 untracked worker reports, nothing of mine
$ git rev-parse HEAD          # start and end — 98a0833f1ede2cf9cef13790388260567a32e868
$ sha256sum <5 measured files> # start and end — identical (listed in §Worker)
```

**PROPOSED (NOT RUN):** `python research/modalities/emc_fourth_cohort_quant.py --check` — refused by design, per the dispatch and W20g's finding; `derive()` writes both TSVs into the tree. Its outcome is **UNKNOWN** and no drift claim is made from it.

**Not attempted, by rule:** the Ensembl cDNA/ncRNA fetch and the vendor TempO-Seq probe manifest. Both remain honest unrecovered sources; no probe, no proxy route, no substitution.

---

## Limitations

- **Nothing here is a clinical claim.** Runs are not samples and samples are not people. There is no wet lab. This is an audit of what published sentences rest on.
- **Every count is a count of persistence, not of biology.** A zero cell means the sequence was not among the counts persisted for that run — missing data, never a measured zero, never a statement about the tumour. That rule is applied to EWSR1's two zeros and NR4A3's three zeros as strictly as anywhere else.
- **Probe identity is UNVERIFIED for the three 50-mers in §4.** Exact identity to a committed cDNA does not establish that the sequence is a TempO-Seq probe; the vendor manifest is not on disk. What is established is that a sequence exactly matching that gene's committed cDNA is in the table and was never offered to the matcher.
- **Whether the matcher would have assigned those sequences is UNKNOWN.** It needs the matcher and therefore the denied Ensembl fetch. I stopped there, as instructed.
- **48 of the 50 `false` rows are UNKNOWN offline** and will stay UNKNOWN without that fetch. Only 7 genes have committed transcript models, and only 3 of them are scored.
- **A "survives" verdict grades the sentence as published, not the route's science.** I did not reopen, re-grade, unblock or promote any route or blocker, did not edit `systems/graph/`, computed no δ, p-value or panel percentile, and authored no repair.
- **`false` rows are also scored against two array series** (`readable_in_array_series`), which I did not audit — that is a different artifact (`emc-expression-panels.json`) and a different denominator.
- Model identity is **SELF-REPORT, not independently verified**.

---

## Tool-call and wall-clock count actually used

**22 tool calls** (all `Bash`; several issued as parallel pairs). **Wall clock 2 min 41 s measured** (`03:11:26Z` → `03:14:07Z`), plus report drafting. Well inside the ~40-call / ~40-minute target; I returned on meeting the stop condition rather than padding.

---

## Next concrete action

**One successor, no network, no repair authorship, disjoint from W20f's and W20g's proposals.** The trace above shows the damage is concentrated in **one inherited sentence** — `emc-fourth-cohort-route-readout.json:14` — and that 13 route sentences inherit it while two (RT-TCRT-CTA `:3110`, RT-MATRIX-ADDRESS's scoping of CSPG4) already say the right thing. The smallest correct fix is therefore a **prose repair in the readout's generator**, not a data change: in `research/modalities/emc_fourth_cohort_route_readout.py`, replace the two-branch disjunction at `_what_a_false_row_is_not` with the three states now established — *offered and unmatched (662)*, *offered and multi-gene (77, excluded for every gene this file scores)*, *never offered to the matcher (211,362 of 213,007; 99.23 % of the table)* — and state the denominator inline the way `routes.json:7235` already does for FN1 ("across the 1,645 probes common to every run"). **It moves no count**: all 67 rows, both TSV hashes, the 862 genes and every route grade are untouched, and no route is reopened. **I did not write it**; it is a code change requiring an owner, the normal `scripts/preflight.sh` commit gate, and — because the generated text lands in `systems/graph/routes.json` and `systems/views/` — the views regeneration proof W09d established.

**Second, smaller, for the module's owner:** add `probe_counts_sha256` to the `--check` drift-key tuple in `emc_fourth_cohort_quant.py` (§6). One line, no scientific content.

**Not recommended, and I am recording the refusal rather than leaving it implicit:** re-deriving the panel at a lower k to see which of the 48 UNKNOWN genes come back. That is the post-hoc iteration W20d refused, it needs the denied fetch, and it would move every committed gene count including the TAF15/FUS values W20e gated against.
