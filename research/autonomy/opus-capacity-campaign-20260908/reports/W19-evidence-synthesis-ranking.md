> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity checks pass: script deterministic (identical output, exit 0 twice), HEAD still at the frozen commit `92abbcb9`, and the only untracked path is the campaign directory the coordinator created — I wrote nothing into the tree.

---

## Worker

**W19**, Lane 19 — source-traceable computable evidence synthesis ranking new EMC research questions.

**Model evidence: SELF-REPORT ONLY, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 01:56:39 UTC 2026` — at end: `Tue Sep  8 02:01:33 UTC 2026`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; no model-identity variable present):

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

(Re-run at end returned the same set; `JAVA_TOOL_OPTIONS`, `no_proxy`/`NO_PROXY`/`npm_config_noproxy` and `GLOBAL_AGENT_NO_PROXY` also match the grep but are proxy plumbing, elided here for length and quoted in full in the tool log.)

---

## Question

**Which currently-open EMC research question should this program ask next, ranked on importance × novelty × achievable-validation × utility, with every input traceable to a source?**

It is open because neither of the repository's two existing ranking mechanisms answers it (see Prior-work check): one ranks *backlog work items that already have a graph record*, the other ranks *drug candidates*. Nothing ranks *questions*.

The single highest-ranked question the synthesis produced, which I believe is the substantive scientific finding here:

> **Q-NR4A2-COVERAGE — What fraction of EMC diagnosed as "NR4A3-rearranged" is actually driven by an NR4A2 fusion, and does every NR4A3-directed agent in this portfolio structurally fail those patients?**

The repository's therapeutic architecture treats NR4A1 and NR4A2 **only as anti-targets to be spared** — `fusion-selective-andgate-degrader-paper.md:54` ("tuned to spare the NR4A1/NR4A2 paralogues"), `:324` ("sparing NR4A2 is best-effort"), `nr4a3-degrader-selectivity-architecture.md:24`. Meanwhile its own retained sources document EMC cases driven by an **NR4A2 fusion**: `HSPA8::NR4A2` (PMID 41315062, Virchows Arch 2025, DOI 10.1007/s00428-025-04352-7) and `FUS::NR4A2` (verbatim at `research/manuscripts/aso/lit-targets-aso-breakpoint-census.json:409`). For such a patient the design requirement is **inverted**: sparing NR4A2 spares the driver. And three routes fail at once — a junction-ASO, an NR4A3-selective degrader and an NR4A3 binder are all blind to an NR4A2 fusion.

My targeted grep for any line combining an NR4A2 fusion with therapeutic coverage/escape/miss returned **no such framing** anywhere in the tree: NR4A2-fusion appears as a citation record and a diagnostic curiosity, never as a coverage gap. That tension is, as far as this session's search reaches, unstated in the repository.

---

## Prior-work check

Commands run and what they showed:

```
rg -n -i "priority|ranking|score|IDEAS|candidate question|backlog" research/ --glob '!.git' -l
```
→ ~40 files. Confirmed the four lane-named files all exist: `research/IDEAS.md`, `research/autonomy/priority.py`, `research/autonomy/priority-weights.json`, `research/autonomy/goals.json`.

```
python3 research/autonomy/priority.py            # exit 0, 415 entries
```

Novelty check on every new source, run as a hit-count sweep (`rg -c` summed per term):

| term | hits in tree | verdict |
|---|---|---|
| `NCC-EMC1` | 69 | already retained |
| `40580361` | 32 | already retained |
| `40828003` | 43 | already retained |
| `42465974` | 32 | already retained |
| `41315062` | 16 | already retained |
| `41755350` | 46 | already retained |
| `40885991` | 93 | already retained |
| `TempO-Seq` | 126 | already retained |
| `PMC13374579` | 3 | already retained |

**This is the load-bearing negative of the session.** Every "new 2025–2026 EMC paper" I retrieved from PubMed was **already in the corpus**. I therefore do **not** claim any retrieved paper as a new finding. What survives as new is not a *source* but a *relation between two retained sources* — Q-NR4A2-COVERAGE above — and the ranking itself.

Closed items I confirmed I am **not** replaying, all carried into the scorer's visible `EXCLUDED` list rather than silently dropped: the NR4A Perspective refusal (not recreated, not rerouted, not relabelled), registry ICD-O, methylation, RT/IPD synthesis, GSE4303/GSE28866 re-read, independent-cohort invention, pazopanib exposure, Sunitinib 2014, and source-index (lane 11's sole ownership).

**Which did I do — extend or invent?** **Extended, from both.** From `research/hypotheses/candidates.json` I reuse the 0–3 ordinal convention, the `tiers` evidence ladder, and — importantly — its explicit disclaimer that the composite is "a transparent triage heuristic ONLY, NOT a probability of success." From `priority.py`/`priority-weights.json` I reuse the discipline that weights live **outside** the code and that a `_forbidden_inputs` list is declared so a banned input cannot silently enter (I carry `aixiv_rating`, `recency`, `axis_d` forward verbatim). I did not fork or modify either.

**Why a new file was nonetheless necessary, stated as a structural fact rather than a preference:** `priority.py` derives every entry from `systems/graph/*.json` route records. A genuinely *new* question has no graph record, so `priority.py` **cannot score it by construction** — it is a scorer over an existing portfolio, not over a candidate space. `candidates.json` scores drugs, not questions. The gap is real.

---

## Method / inputs

- Repo, read-only, frozen at HEAD `92abbcb905cacf07f14b238db50d1b98f6590374` (verified at end of run).
- `systems/graph/routes.json` — 83 routes; I computed blocker-inheritance counts myself rather than quoting the weights file's stale figure.
- `research/hypotheses/candidates.json` (14 drug candidates, `scoring`/`tiers` schema), `build-candidates.mjs`, `research/autonomy/priority-weights.json`, `research/autonomy/priority.py`.
- PubMed via MCP (`mcp__PubMed__search_articles`, `get_article_metadata`): query `extraskeletal myxoid chondrosarcoma NR4A3`, 2024–, 96 total hits, 25 retrieved, metadata pulled for 12.
- Python 3.11.15; scorer at `/tmp/claude-0/w19/rank_questions.py` (stdlib only, no network, $0).

**Egress, recorded honestly.** Direct data-existence verification against public repositories **failed and was not routed around**. `curl` to `www.ebi.ac.uk`, `depmap.org`, `cbioportal.org`, `rest.uniprot.org` all returned HTTP code `000`; `curl -sS "$HTTPS_PROXY/__agentproxy/status"` shows the cause verbatim:

```
"kind": "connect_rejected",
"detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
"host": "www.ebi.ac.uk:443"   (also ftp.ebi.ac.uk:443, depmap.org:443, cbioportal.org:443)
```

This is a **gateway policy denial, i.e. UNKNOWN — not evidence of absence**, and it is scored as such (it is precisely why `Q-PARALOGUE-DDG-PUBLIC` gets achievable-validation = 1). PubMed via MCP is a *genuinely different* route, not a replay of the denied one.

---

## Result

### Ranked candidate questions — computed output

`I`=importance, `N`=novelty, `V`=achievable-validation, `U`=utility, each 0–3. `GEO` = weighted geometric mean (primary). `WSUM` = weighted sum (cross-check). **All rows are `PREDICTION`** in the brief's taxonomy — these are *judgements*, not measurements (see Limitations). n=10 candidates; no uncertainty interval is defined because the axes are ordinal judgements, not sampled quantities — the sensitivity sweep below substitutes for one.

| # | id | I | N | V | U | GEO | WSUM | class |
|---|---|---|---|---|---|---|---|---|
| 1 | Q-NR4A2-COVERAGE | 3 | 3 | 2 | 3 | 2.656 | 2.70 | PREDICTION |
| 2 | Q-EMC-DATA-BOTTLENECK | 3 | 1 | 3 | 3 | 2.544 | 2.70 | PREDICTION |
| 3 | Q-SGA-DEPENDENCY | 3 | 2 | 2 | 2 | 2.305 | 2.35 | PREDICTION |
| 4 | Q-PEERJ-EXTERNAL-31 | 2 | 2 | 2 | 3 | 2.169 | 2.20 | PREDICTION |
| 5 | Q-IMMUNE-STRATIFY | 2 | 2 | 2 | 2 | 2.000 | 2.00 | PREDICTION |
| 6 | Q-CELLLINE-ACCESS | 2 | 1 | 2 | 2 | 1.803 | 1.85 | PREDICTION |
| 7 | Q-JUNCTION-HLA | 2 | 1 | 3 | 1 | 1.772 | 1.95 | PREDICTION |
| 8 | Q-CISTROME-EMC | 3 | 1 | 1 | 2 | 1.687 | 1.90 | PREDICTION |
| 9 | Q-PARALOGUE-DDG-PUBLIC | 2 | 1 | 1 | 2 | 1.464 | 1.55 | PREDICTION |
| 10 | Q-MRI-SURROGATE | 1 | 2 | 1 | 1 | 1.110 | 1.15 | PREDICTION |

### Source traceability for each axis input

| id | question | source for the inputs | data exists? |
|---|---|---|---|
| Q-NR4A2-COVERAGE | NR4A2-fusion EMC coverage gap | PMID 41315062 (DOI 10.1007/s00428-025-04352-7); `lit-targets-aso-breakpoint-census.json:409`; PMID 41755350; repo anti-target framing at `fusion-selective-andgate-degrader-paper.md:54,324` | `SECONDARY` — case reports exist and are retained. Prevalence **UNKNOWN** |
| Q-EMC-DATA-BOTTLENECK | Is BLK-NO-EMC-DATA $0-removable? | **`PRIMARY` (computed by me this session)**: 42 of 83 routes inherit `BLK-NO-EMC-DATA`; `research/IDEAS.md:201-208` | yes, graph is in-tree |
| Q-PEERJ-EXTERNAL-31 | Are the 31 external EMC cases retrievable and independent of GSE4303/GSE28866? | PMID 42465974 / PMC13374579 / DOI 10.7717/peerj.21497 | **UNKNOWN — not verified**, repository egress 403 |
| Q-SGA-DEPENDENCY | Recurrent druggable secondary alteration? | PMID 40828003, DOI 10.1002/gcc.70076 | `SECONDARY`, abstract retrieved; full table not verified |
| Q-IMMUNE-STRATIFY | B-cell-high phenotype reproducible? | PMID 42465974 (B-cell p=0.005; mIF n=2; **authors report their own LASSO-Cox model overfits**) | `SECONDARY`, n=12 + 31 external |
| Q-CELLLINE-ACCESS | Machine-readable 221-drug screen? | PMID 40580361; `method-watch.md:456` records it **paywalled, no accession**; `what-a-civilian-can-buy.md:358` records MTA-only | `UNKNOWN`, recorded paywalled |
| Q-JUNCTION-HLA | Junction peptide presentation under partner heterogeneity | RT-JUNCTION-NEOANTIGEN recorded `complete` | computable at $0 |
| Q-CISTROME-EMC | Chromatin gap closable by non-antigen-labelled deposit? | `nr4a3-fusion-transcriptional-output.md:1269` — absence inference **retracted** 2026-08-08 after GSE243553/PMID 39048711; narrower claim stands | wide 179-endpoint search already run |
| Q-PARALOGUE-DDG-PUBLIC | Public NR4A LBD structures for a ΔΔG benchmark? | BLK-PARALOGUE-DDG measured by me: 9 of 83 routes | **UNKNOWN — 403 CONNECT to ebi.ac.uk** |
| Q-MRI-SURROGATE | MRI features vs fusion partner | PMID 41074947, DOI 10.1007/s00256-025-05050-w, 44 patients | per-patient imaging not public |

### Blocker inheritance — measured, not quoted

Computed from `systems/graph/routes.json` (n=83 routes), `PRIMARY`:

```
42 BLK-NO-EMC-DATA      17 BLK-NO-WET-LAB       14 BLK-NOT-FUSION-SELECTIVE
10 BLK-ANTIGEN-COLD      9 BLK-PARALOGUE-DDG     9 BLK-NO-CURATED-CLINICAL-DATA
 8 BLK-R4-BINDS          5 BLK-TERNARY-GEOMETRY
```

Note a discrepancy worth flagging to the coordinator: `priority-weights.json` states "`BLK-NO-EMC-DATA` alone is inherited by 38 of 77 routes". On today's tree it is **42 of 77→83**. The weights file's figure is dated 2026-09-02; the ratio is materially unchanged (0.494 → 0.506), so nothing in the leverage-cap argument is disturbed — but the number is stale.

### Visible exclusions (9)

Enumerated and then excluded with reason, per lane instruction — not silently dropped: `Q-RT-CHEMO-EMC` (RT/IPD synthesis checkpoint did not admit its paper), `Q-ICD-O-REGISTRY` (user rejected), `Q-METHYLATION` (deprioritized), `Q-GSE-REREAD` (rediscovery is not new data), `Q-NR4A-PERSPECTIVE` (**content-policy refusal — retained, not rerouted, not relabelled**), `Q-PAZOPANIB-EXPOSURE`, `Q-SUNITINIB-2014` (denied routes, no new route available), `Q-NEW-COHORT` (cohorts must not be invented), `Q-SOURCE-INDEX` (lane 11 sole owner).

### Sensitivity — the ranking is NOT robust, and this is the honest headline

80 weight vectors over {0.10 … 0.50}⁴ summing to 1.0:

- **70 of 80 (87.5%)** reorder the baseline top three.
- **58 of 80 (72.5%)** change top-three *membership*.
- **Rank-1 identity across all 80: `Q-NR4A2-COVERAGE` 66, `Q-EMC-DATA-BOTTLENECK` 14, nothing else ever.**
- The two functional forms **disagree** on top-3 order: under the weighted sum, Q-EMC-DATA-BOTTLENECK and Q-NR4A2-COVERAGE **tie exactly at 2.70** and the tiebreak flips them.

**So: yes, reweighting reorders the top three — badly.** What the computation actually supports is a robust **top-two set** {Q-NR4A2-COVERAGE, Q-EMC-DATA-BOTTLENECK}, not a robust ordering. Any claim that this synthesis identifies *the* single best question would be an overread of its own output.

---

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24, Python 3.11.15, stdlib only, no network, $0. cwd `/tmp/claude-0/w19` (outside the repository).

```
$ python3 --version
Python 3.11.15
$ python3 rank_questions.py
... (ranked table, sensitivity block and 9 exclusions as reproduced above) ...
EXIT=0
```

Determinism check:
```
$ python3 rank_questions.py > a.txt; python3 rank_questions.py > b.txt; diff -q a.txt b.txt
DETERMINISTIC (exit 0/0)
```

Write-isolation check:
```
$ git status --porcelain
?? research/autonomy/opus-capacity-campaign-20260908/
$ git rev-parse HEAD
92abbcb905cacf07f14b238db50d1b98f6590374
```
The single untracked path is the campaign briefing directory that pre-existed my session. **I created and modified no file under `/home/user/Rare-cancers`, and ran no git write operation.**

Egress probe, **RUN, negative**: four `curl` calls returned `000`; proxy status returned `connect_rejected / gateway answered 403 to CONNECT` for ebi.ac.uk, ftp.ebi.ac.uk, depmap.org, cbioportal.org.

**PROPOSED (NOT RUN):** retrieval of the PeerJ 42465974 supplementary case list; any DepMap/cBioPortal/PDBe query; any test of Q-NR4A2-COVERAGE against a real EMC case series. `scripts/preflight.sh` was **not** run (dispatch did not direct it).

### The scorer

`/tmp/claude-0/w19/rank_questions.py` — returned inline per write isolation. Reproduced in full in the tool log above; its structure is: `WEIGHTS` (each weight carrying its own `why` justification), `FORBIDDEN_INPUTS` carried forward from `priority-weights.json`, the 10-candidate list `C` with an `ev` source string per candidate, the 9-item `EXCLUDED` list, `geo()`/`wsum()` scoring functions, and a `main()` that prints the table, the cross-check, the 80-vector sensitivity sweep and the exclusions. The weight justifications, verbatim:

- **importance 0.35** — "How much a patient outcome moves if answered. CLAUDE.md §0 makes patient outcome the objective, so it carries the largest weight."
- **achievable_validation 0.30** — "Whether THIS program, with no wet lab and restricted egress, can actually close the question. Nearly as large as importance because an unvalidatable question yields nothing regardless of how important it is."
- **utility 0.20** — "How many other routes/blockers the answer unblocks — the `blocker_leverage` idea from priority-weights.json, applied to questions."
- **novelty 0.15** — "Smallest on purpose. Novelty is what makes a result publishable, not what makes it useful; weighting it higher is how a program drifts to novel-but-useless."

The multiplicative (geometric) form is primary because it encodes a **veto**: a 0 on any axis zeroes the score, which is the correct behaviour for a question that cannot be validated however important it is.

---

## Limitations

1. **These scores are judgements, not measurements.** The operating protocol is explicit that planning scores are judgements, not evidence. Every I/N/V/U value was assigned by me. The *computation* over them is real and reproducible; the *inputs* are opinion. A reproducible arithmetic over subjective inputs is still subjective.
2. **The ordering is not robust.** 87.5% of tested weightings reorder the top three; the two functional forms disagree at rank 1–2. Only the top-*two set* survives reweighting. Do not treat rank 3–10 as meaningfully ordered.
3. **No new source was found.** Every 2025–2026 EMC paper retrieved was already in the corpus. The contribution is a *relation* between retained sources plus the ranking, not new literature.
4. **Data existence is largely UNVERIFIED.** Gateway 403s blocked every public-repository check. Rows marked UNKNOWN are unknown, not absent — and the scorer penalises them via V rather than pretending otherwise.
5. **Q-NR4A2-COVERAGE prevalence is UNKNOWN.** I counted fusion-partner *string mentions* in a literature-target file and deliberately do **not** report them as case frequencies — that file is a query corpus, not a per-case table. At least two distinct NR4A2-fusion EMC reports are retained; the denominator is unknown. The coverage-gap *tension* is real; its *size* is not established.
6. **Nothing here is clinical evidence.** No computation establishes efficacy, safety, selectivity or clinical readiness. There is no wet lab.
7. **This does not contradict the repo's own conclusion at `IDEAS.md:201-208`** that idea-generation is not the constraint — the bottleneck is model/data access. A ranked question list does not remove that bottleneck. Read Q-NR4A2-COVERAGE as a *correction to an existing design requirement* (cheap, in-tree, actionable) rather than as a new experimental program.
8. Wall-clock ran ~5 min over the ~40 min target.

---

## Stop condition

**Set:** a computed, source-traceable ranked candidate table with visible exclusions and a run sensitivity check.

**MET.** Table computed (exit 0, deterministic), 10 candidates each traced to a named source or an in-tree measurement, 9 exclusions printed with reasons, sensitivity sweep of 80 weight vectors run — and reported as *negative for ordering robustness*, which is the honest result rather than the flattering one.

---

## Tool-call and wall-clock count actually used

**25 tool calls** (target ~40). **Wall clock 01:56:39Z → 02:01:33Z ≈ 5 minutes of tool time**; total turn duration modestly longer. Under budget on calls.

---

## Next concrete action

**One task: test Q-NR4A2-COVERAGE against the repository's own fusion-partner census and write the correction if it holds.** Specifically — enumerate every EMC case with a named fusion partner across the retained breakpoint/citation corpora (`lit-targets-aso-breakpoint-census.json`, `fusion-junction-aso-references.json`, the retained case series PMIDs 41755350 / 41644428 / 41315062), classify each as NR4A3-partnered vs NR4A2-partnered, and report the NR4A2 numerator with an explicit, honest denominator. If any NR4A2-fusion EMC case survives that count — and at least two appear to — then the design requirement stated as "spare NR4A1/NR4A2" in `fusion-selective-andgate-degrader-paper.md`, `nr4a3-degrader-selectivity-architecture.md` and requirement R7 needs a scoped caveat: *sparing NR4A2 is correct for NR4A3-driven EMC and inverted for the NR4A2-fusion subset*. That is a $0, in-tree, patient-relevant correction with a checkable numerator, and it belongs to whoever owns the degrader selectivity architecture — not to me, since I hold no write access.

result: W19 delivered a computed, source-traceable ranking of 10 open EMC research questions (deterministic, exit 0) that extends the repo's two existing scoring mechanisms rather than duplicating them; its top question — that NR4A2-fusion EMC patients are structurally missed by every NR4A3-directed agent while the repo's design requirement says to *spare* NR4A2 — is unstated in the tree, and the sensitivity sweep honestly reports that 87.5% of reweightings reorder the top three, so only a top-two set is robust.
