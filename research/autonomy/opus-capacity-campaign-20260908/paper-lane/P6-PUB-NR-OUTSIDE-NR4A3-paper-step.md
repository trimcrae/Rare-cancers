<!-- collected 2026-09-08T05:19:29Z by campaign coordinator; agent id aa1b76c887c857060; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aa1b76c887c857060.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

All checks complete; scratch directory deleted; tree untouched.

## Worker

**P6 — PAPER lane**, campaign OPUS-CAPACITY-CAMPAIGN-20260908. Candidate: `PUB-NR-OUTSIDE-NR4A3`.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). This is a self-report from the system prompt, not an observed served-model measurement; the coordinator should extract the actual per-child runtime model from the transcript.

Start `date -u`: `Tue Sep  8 05:10:21 UTC 2026` · HEAD `0d05cb7b3bf27921cceeb76bd69873ed89eb9fd6` · `git status --porcelain`: empty.
End `date -u`: `Tue Sep  8 05:14:00 UTC 2026` · HEAD `997bc9e769da6bf606392941d46d20b319beab85` (coordinator commits advanced it mid-run; campaign directory only) · `git status --porcelain`: 0 lines.

Literal output of the env command (run at start; secrets redacted by the required `sed`):

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ...
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

(Three long proxy/no-proxy values are elided at `...` for length; they were printed in full and contain no credentials.)

## Stop condition (stated up front)

**Stop when both route gradings have been checked against their own primary records, the reach arithmetic has been independently recomputed, the surviving general claim has been graded, and a Results + Limitations draft exists in this response.** **MET.** No refusal was encountered. W25 scope was never entered: no `reports/W25-*`, no GSE243553, and the one file in `research/manuscripts/fusion-output/` bearing that accession (`gse243553-eno3-overlap-2026-08-08.md`) was deliberately not opened.

## Question

Is `PUB-NR-OUTSIDE-NR4A3` writable today, and does its own record's grading of its two routes survive a check against the primary artifacts those routes cite? Concretely: (a) is the dormancy route really unreadable on both readable platforms, and is "no further expression work can close it" true as written; (b) does the partner route's reach arithmetic reproduce; (c) is the surviving general claim — that a fusion imports the 5′ partner's regulatory input, never NR4A3's own — a measurement, a retrieved statement, or a structural argument?

It is open because the record is `state: outlined` with no manuscript file, and because both routes' grading text was written before at least one artifact that bears on it (`hspa8-promoter-hormone-grade.json`) existed.

## Prior-work check

Commands run from `/home/user/Rare-cancers` at HEAD `0d05cb7b`:

- `rg -n -i "NR2F1|dormancy" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**' -l` — 30 files; the owning artifacts are `research/modalities/nr2f1-dormancy-lane.json` and `research/modalities/census-route-expression-grading.json`.
- `rg -n -i "partner's promoter|imports? (a|the) regulatory|IEG promoter" …` — 14 files carry the general claim in prose or code comments; **none is a manuscript**.
- `git ls-files | rg -i "hormone-partner|nr2f1"` — 5 files, all under `research/modalities/`, `research/manuscripts/occupancy/` or `systems/views/`. **There is no `research/manuscripts/**` document for either route.** The paper is genuinely unwritten, not a rewrite.
- Publication-record scan of `systems/graph/publications.json` for neighbouring homes: `PUB-FUSION-OUTPUT` (drafted) claims a gene-set calibration result; `PUB-FUSION-PARTNER` (drafted) claims partner-stratified prognosis/response. **Neither owns the fusion-architecture claim**, so this candidate does not duplicate them.

Closed items confirmed and **not** replayed: the refused NR4A Perspective (I am not writing a perspective, a venue-shifted perspective, or an NR4A pharmacology review — the deliverable below is a negative-results and architecture note on two graded routes); Brenca case identities; Hofvander/EGA; the rejected registry ICD-O paper; GSE4303/GSE28866 rediscovery (I read *derived committed artifacts*, not raw series, and claim no new data). Lane-2 statistics on `emc-expression-panels.json` were not extended — I read two committed gene rows and one committed group score, and computed no new statistic on that substrate. W25/GSE243553 not touched.

## Method and inputs

Read-only reads of the live checkout (no corpus reads were needed; every path below resolves live):

| input | what it supplied |
|---|---|
| `systems/graph/publications.json` → `PUB-NR-OUTSIDE-NR4A3` | the record under test |
| `research/modalities/nr2f1-dormancy-lane.json` | dormancy route's own primary record (F1–F5, disease-fit argument) |
| `research/modalities/emc-expression-panels.json` → `gene_reads.NR2F1`, `gene_reads.NR4A3`, `platforms` | the probe-level absence, and the readable positive control |
| `research/modalities/census-route-expression-grading.json` → `routes["RT-NR2F1"]` | the graded verdict and the dormancy-context group score |
| `research/modalities/census_route_expression_grading.py:332-350`, `:1-80` | the two platform identities and the governing "not a reading of absence" rule |
| `research/modalities/hormone-partner-lane.json` | partner map, reach block, 12 partner rows, tier summary |
| `research/modalities/hspa8-promoter-hormone-grade.json` | the last ungraded partner promoter (post-dates the record's text) |
| `research/manuscripts/degrader/nr4a3-emc-biology-evidence.md:29-31` | the two cohorts' partner distributions with identifiers |
| `research/manuscripts/fusion-partner/partner-event-counts-2026-08-08.md` | retrieval status of the cohort tables |
| `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` | cohort citation metadata (PMIDs, OA status) |
| `research/modalities/emc-data-level-sweep.json`, `emc_data_level_sweep.py:100-135` | the one *direct measurement* attempt at the architecture signature |
| `systems/views/L2-rt-nr2f1.md`, `L2-rt-hormone-partner.md` | the generated route views (consistency check only) |

Tools: `python3` (stdlib `json`, `math`), `rg`, `sed`, `git` (read-only). No network, no paid API, no GPU. `research/modalities/atr_hrd_sarcoma_series.py` was never invoked, with or without `--check`. `scripts/preflight.sh` was not run.

## Route-by-route grading verification

| # | Claim as the record states it | What was actually looked up | Exact path | Grade | Verdict on the record's wording |
|---|---|---|---|---|---|
| D1 | Dormancy receptor "has no probe on either readable platform" | `gene_reads.NR2F1` → **GPL6244: `n_probes_mapping: 0`, `readable: false`**; **GPL3290: `n_probes_mapping: 0`, `readable: false`** | `research/modalities/emc-expression-panels.json` → `gene_reads.NR2F1` | **PRIMARY** (computation on committed series matrices, reproduced from the committed artifact) | **CONFIRMED.** The two platforms are named below. |
| D2 | The two readable platforms | **GPL6244**, series `GSE24369_series_matrix.txt.gz`, 6 EMC vs 29 comparator sarcomas, 28,459 probes, 20,235 mapped to a symbol (rate 0.711); **GPL3290**, series `GSE4303-GPL3290_series_matrix.txt.gz`, 10 EMC vs 6 comparator, 43,008 probes, 27,197 mapped (rate 0.6324) | same file, `platforms`; `census_route_expression_grading.py:31-35` | **PRIMARY** | Confirmed and now named rather than asserted. |
| D3 | The absence is an instrument limit, not a reading of absence | The same panel reads **NR4A3 as readable on both** (1 probe each: `8156848` on GPL6244, `38769` on GPL3290), and higher in EMC on GPL6244 by **0.7415 SD**, Welch t = 4.662, df = 7.2, n = 6 vs 29 | same file, `gene_reads.NR4A3` | **PRIMARY** | Confirmed, and materially strengthened: a gene-specific null beside a working positive control on the same arrays is a much better-supported "unreadable" than a bare null. |
| D4 | "an instrument limit that **no further expression work can close**" | The artifact's own `route_action` reads: *"keep; the next observation must come from a platform that carries the probe."* The `why_not_readable` field also states the null conflates "array carries no probe" with "probe identifier did not resolve" (29% and 37% of probes unmapped respectively) | `census-route-expression-grading.json` → `routes["RT-NR2F1"].route_action`; `emc-expression-panels.json` → `gene_reads.NR2F1.*.why_not_readable` | **UNSUPPORTED AS WRITTEN** | **CORRECTION REQUIRED.** No *further work on these two series* can close it. Any platform carrying an NR2F1 probe, or a probe-identifier re-resolution on these arrays, could. The record over-states a live instrument limit as a permanent one. |
| D5 | The receptor "has the published tool compound this program's own receptor never had" | The compound (C26) was **discovered by AutoDock 4 + eHiTS docking into a MODELLER homology model built on RXRα, PDB 1FM6, ~40% identity**; there is **no experimental NR2F1 or NR2F1-LBD structure**; and **no Kd, SPR, ITC, thermal shift or radioligand displacement against NR2F1 protein appears anywhere in the retrieved text**. Real cellular and in-vivo data exist (RARE-luciferase 2.4-fold; CRISPR knockout abolishes the effect; CAM tumour NR2F1+ cells ~4% → 42%) | `research/modalities/nr2f1-dormancy-lane.json` → `evidence.F1_no_experimental_nr2f1_structure`, `.F2_c26_is_not_a_known_answer`; sources PMID 34812843 / PMC8614154, PMC9024734, PMC10955615 | **RETRIEVED** for the compound's existence and its cellular/in-vivo readouts; **UNSUPPORTED** for "tool compound" in the sense of a probe with measured target engagement | **CORRECTION REQUIRED.** The repository's own artifact grades the capability-transfer claim **REFUTED**. The paper may say a small molecule with published cellular and in-vivo dormancy data exists and is a reagent-availability fact; it may not call it a validated chemical probe, and it must not call it a treatment. |
| D6 | Route context (retained, positive) | A **repo-curated** dormancy-associated context set (7/7 genes readable) is higher in EMC on **both** platforms: GPL6244 Δ 0.6323 SD, t = 11.017, df = 10.5, n = 6 vs 29; GPL3290 Δ 0.6377 SD, t = 3.62, df = 12.1, n = 10 vs 6 | `census-route-expression-grading.json` → `routes["RT-NR2F1"].panel_groups` | **PRIMARY** computation on a **hand-curated, non-published gene list** (the panel says so: *"REPO-CURATED pathway-membership list… NOT a published gene set"*), uncorrected for multiple testing | Confirmed; must travel with both caveats. |
| P1 | A hormone-responsive 5′ partner is reported in **one EMC patient in the world literature** | `world_literature_emc_cases: 1` — PGR::NR4A3, **PMID 36103645 / PMC9489176** (Wilbur HC et al., *JCO Precis Oncol* 2022;6:e2200039). The index case is EWSR1-FISH-negative cellular-variant EMC | `research/modalities/hormone-partner-lane.json` → `reach`, `partners[PGR]`; identifier cross-checked in `research/manuscripts/aso/fusion-junction-aso-submission-references.md:34` | **RETRIEVED** (n = 1 published case) | **CONFIRMED.** The second oestrogen-axis partner, **GREB1::NR4A3**, is real (PMC7489201: `GREB1-NR4A3 (N = 1)`; PMC7490989) but is a **uterine** tumour — it adds zero EMC patients. |
| P2 | **Zero** of the partner-genotyped cases the cited cohorts cover | **Huang 2023, PMID 36948401, n = 58**: EWSR1 46 (79%), TAF15 9 (16%), TCF12 2 (3%), 1 unpartnered → 58/58 NR4A3-rearranged, **0 PGR, 0 GREB1**. **Agaram, *Hum Pathol* 2014, PMC4015728, n = 26**: 16 / 7 / 1, **0 PGR, 0 GREB1**. Pooled **n = 84, k = 0** | `research/manuscripts/degrader/nr4a3-emc-biology-evidence.md:29-31` (owner); arithmetic in `hormone-partner-lane.json` → `reach.per_cohort`, `reach.pooled` | **RETRIEVED** counts; **PRIMARY** for the interval computed on them | **CONFIRMED.** |
| P3 | The reach arithmetic | Independently recomputed the Wilson score upper bound for k = 0 at z = 1.959963984540054: n = 58 → **0.062117855787202914**; n = 26 → **0.1287289218592153**; n = 84 → **0.04373172841465988**. All three reproduce the committed values to the last printed digit | recomputation vs `hormone-partner-lane.json` → `reach` | **PRIMARY, REPRODUCED** | **CONFIRMED.** The travelling number is: hormone-responsive-partner fraction of EMC **bounded above at ~4.4%**, on **0 events in 84 genotyped cases**. Non-overlap of the two cohorts is **assumed and not verified**, so 4.4% is the optimistic end. |
| P4 | The **dominant partner** has no retrieved druggable input | Dominant partner is **EWSR1** — 46/58 (79%) in Huang, 16/26 in Agaram, and *"Seventy percent of EMC are characterized by a chromosomal rearrangement involving the NR4A3 gene… with EWSR1"* (PMC9489176). Tier `NO_INDUCIBLE_INPUT_RETRIEVED`, `druggable_input: false`, over **345 open-access full texts of 530 retrieved records** | `hormone-partner-lane.json` → `partners[EWSR1]`, `corpus` | **RETRIEVAL NEGATIVE** (not a measured absence; 185 records were not open-access) | **CONFIRMED**, with the bound stated. |
| P5 | Partner-map completeness | 12 partners with ≥1 retrieved source; **9 of 10 EMC partners** graded `NO_INDUCIBLE_INPUT_RETRIEVED`; **1 of 10 EMC partners** (PGR) hormone-responsive; ACTB, CARMN, SLCO5A1 carried as `PARTNER_NOT_RETRIEVED` after zero sources over 345 full texts | `hormone-partner-lane.json` → `tier_summary`, `counts`, `corrections_to_3_12` | **RETRIEVED** | Confirmed. |
| P6 | *(Not in the record's text — newer evidence)* | **HSPA8**, the one partner whose family plausibly carried an inducible input, has since been graded: 7/7 + 8/8 + 13/13 PubMed abstracts read, **not one maps an ERE/ARE/PRE/GRE in the HSPA8 promoter**; the only localised cis-elements in a mammalian *hsc70* promoter are **Sp1 sites** | `research/modalities/hspa8-promoter-hormone-grade.json` → `verdict` | **RETRIEVAL NEGATIVE**, explicitly self-labelled *"an absence of asking"*, not a measured absence | **The record's `why_not_written` is out of date**: this row closed the last $0 item the partner route named. It strengthens the negative and should be folded in. |

## The surviving general claim and its evidence grade

**Claim:** *the regulatory input a NR4A3 fusion imports is the 5′ partner's, never NR4A3's own.*

**What supports it, exactly:**

1. **A 12-partner annotation across three tumour types** — `research/modalities/hormone-partner-lane.json` → `partners[]`. In every retrieved case the imported element belongs to the partner locus: nine EMC partners contribute their own promoters; PGR contributes an oestrogen-driven promoter; GREB1 contributes a canonical ER-target promoter in uterine sarcoma; and the SCPP cluster at 4q13 contributes a **salivary secretory-protein enhancer** juxtaposed to the NR4A3 TSS in acinic cell carcinoma — enhancer hijacking of *wild-type* NR4A3, the same principle by a different element. Grade: **RETRIEVED** (published breakpoint and rearrangement architecture, annotated here).
2. **Published breakpoint architecture in the index EMC case**: PGR exon 2 fused to the **5′ UTR of NR4A3 (exon 2)** — PMC9489176, quoted in the same artifact. The fusion allele therefore does not carry NR4A3's own promoter. Grade: **RETRIEVED**.
3. **The corollary the repository already draws**: NR4A3 is a MAPK-induced immediate-early gene, so lowering fusion transcription with an upstream-signalling inhibitor is *architecturally* impossible — the fusion allele does not use NR4A3's IEG promoter. Same argument closes β-adrenergic, angiotensin-II and serum-response modulation of the fusion. Source: `hormone-partner-lane.json` → `⛔_the_clean_negative_that_travels_with_this_route`. Grade: **STRUCTURAL ARGUMENT** built on (1) and (2).
4. **The one attempt to make it a measurement, and its result.** `research/modalities/emc_data_level_sweep.py` defines a 5′-depletion signature — a gene whose downstream junctions carry coverage while its own 5′-most junctions carry none — and searched the public splice-junction index for it. **The instrument worked and the target read null.** At the pre-registered operating point the positive controls fired (ERG **252.0×** enrichment, 191 candidates in 681 samples; FLI1 **13.4×**), the negative panel behaved, the absent control returned 0 records — and **NR4A3 had only 219 samples in that regime against a needed pool of ~1,498, giving `TARGET_UNDERPOWERED_AT_THE_OPERATING_POINT`**. At the best-powered comparison, over 34,013 samples, NR4A3 **does not exceed the ordinary-gene envelope at any of 288 comparable cells** (ratio **0.6722**, Katz 95% CI 0.6393–0.7068). Source: `research/modalities/emc-data-level-sweep.json` → `arms.snaptron_junction_index`. Grade: **PRIMARY, NEGATIVE/UNDERPOWERED** — an absent reading, not a reading of absence.

**Honest grade of the claim: a STRUCTURAL ARGUMENT over retrieved published architecture, corroborated by a 12-partner annotation across three tumour types, and NOT corroborated by the one direct measurement this repository attempted.** It is not a measurement and must not be dressed as one.

**Scope.** The evidence supports it for **NR4A3 fusions specifically**, across three diseases (extraskeletal myxoid chondrosarcoma; GREB1-/PGR-rearranged uterine tumours; salivary acinic cell carcinoma). It does **not** support "fusion architecture generally" — FLI1 and ERG appear here only as instrument positive controls, not as evidence, and no systematic survey of other fusion families was done. Any sentence beyond the NR4A3 family is a hypothesis.

## Drafted section

> ### Results
>
> #### 1. The dormancy-receptor route is unread, and the limit is the instrument
>
> The route's precondition — is the dormancy receptor NR2F1 present in EMC at all — cannot be answered from either expression series this programme can read. On GPL6244 (series `GSE24369_series_matrix.txt.gz`; 6 EMC against 29 comparator sarcomas; 28,459 probes, 20,235 mapped to a gene symbol) **no probe maps to NR2F1** (`n_probes_mapping: 0`). On GPL3290 (series `GSE4303-GPL3290_series_matrix.txt.gz`; 10 EMC against 6 comparator; 43,008 probes, 27,197 mapped) the result is the same (`n_probes_mapping: 0`). Both rows and both platform descriptions are in `research/modalities/emc-expression-panels.json` (`gene_reads.NR2F1`, `platforms`), and the graded route verdict is `UNREAD` in `research/modalities/census-route-expression-grading.json` (`routes["RT-NR2F1"]`).
>
> The null is gene-specific rather than a pipeline failure. On the same two arrays NR4A3 is read by a single probe each (`8156848`, `38769`), and on GPL6244 it is higher in EMC by 0.7415 SD units of the array (Welch t = 4.662, df = 7.2; n = 6 vs 29) — the disease-defining over-expression recovered as a positive control (`gene_reads.NR4A3`, same file). An instrument that recovers the expected positive and returns nothing for the receptor of interest has reported an **absent reading, not a reading of absence**.
>
> The limit is bounded, and we state its bound rather than its rhetoric. Each platform's probe-to-symbol mapping is incomplete (0.711 and 0.6324), so "no probe maps" conflates *the array carries no probe* with *the probe identifier did not resolve* — the artifact records this in its own `why_not_readable` field. The reading is therefore closed **for these two series**, not closed in principle: a platform carrying an NR2F1 probe, or a re-resolution of these arrays' unmapped identifiers, would answer it. The route's own recorded next step says exactly this.
>
> One adjacent observation survives and is reported separately because it is weaker than it looks. A **repository-curated**, hand-listed dormancy-associated context set — not a published signature — reads higher in EMC on both platforms (GPL6244: +0.6323 SD, t = 11.017, df = 10.5, 7/7 genes readable; GPL3290: +0.6377 SD, t = 3.62, df = 12.1, 7/7 readable; uncorrected for multiple testing). A programme-level elevation is not a reading of the receptor, and we do not treat it as one.
>
> Finally, a correction to the premise that made this route attractive. It was proposed on the basis that this receptor, unlike the one that defines the disease, has a published small molecule. Retrieval does not support the stronger reading of that premise: there is **no experimental structure of NR2F1 or its ligand-binding domain** (PMID 34812843 / PMC8614154, in its own words; corroborated by PMC9024734 and PMC10955615); the compound was **discovered by docking into a homology model built on RXRα at ~40% identity**; and **no binding constant against NR2F1 protein — no Kd, SPR, ITC, thermal shift or radioligand displacement — appears in the retrieved record**, target engagement being inferred from the knockout-dependence of a cellular effect. Real cellular and in-vivo data exist. This is a statement about **reagent availability and its provenance**, and it is not a claim of efficacy, selectivity, safety, therapeutic window or clinical readiness in this or any disease (`research/modalities/nr2f1-dormancy-lane.json`, F1–F2).
>
> #### 2. The hormone-responsive-partner route is closed on reach
>
> A hormone-responsive 5′ partner of NR4A3 is reported in **one** EMC patient in the reachable literature: a PGR::NR4A3 fusion joining PGR exon 2 to the 5′ untranslated region of NR4A3 exon 2 (PMID 36103645 / PMC9489176). The index tumour was an EWSR1-FISH-negative cellular-variant EMC — the variant in which non-EWSR1 partners concentrate, and one a break-apart assay would not have called fusion-positive.
>
> Against that single case stand the two partner-genotyped cohorts this programme cites. Huang et al. 2023 (PMID 36948401) typed **58** EMC: EWSR1 46 (79%), TAF15 9 (16%), TCF12 2 (3%), one NR4A3-rearranged with no partner identified. Agaram et al., *Hum Pathol* 2014 (PMC4015728) typed **26**: 16 / 7 / 1. **Neither cohort contains a single hormone-responsive-partner case.** Pooling them as non-overlapping strata gives **0 events in 84 genotyped patients**; the Wilson 95% score interval is 0–**4.4%** (0–6.2% at n = 58; 0–12.9% at n = 26). We recomputed all three bounds independently and they reproduce the committed values exactly (`research/modalities/hormone-partner-lane.json`, `reach`; cohort distributions owned by `research/manuscripts/degrader/nr4a3-emc-biology-evidence.md` §Hypothesis 2). Zero events bound a rate; they do not measure one, and both cohorts genotyped by targeted assays that the index case's own authors state would have missed their case — a blind spot that widens the honest interval rather than raising the estimate.
>
> The second oestrogen-axis partner does not help. GREB1::NR4A3 is real (PMC7489201; PMC7490989) but every retrieved case is a uterine tumour. Both hormone-responsive partners of NR4A3 are gynaecologic-tract events; one of them has appeared once in EMC.
>
> And the partner that actually dominates the disease imports nothing addressable. EWSR1 accounts for 46/58 and 16/26 of the typed cases above and is described as ~70% of EMC in review (PMC9489176). Across **345 open-access full texts drawn from 530 retrieved records**, **no source characterises the EWSR1 promoter as responsive to any druggable stimulus**; the FET genes are described throughout as ubiquitously expressed. Nine of the ten EMC partners are graded identically (`NO_INDUCIBLE_INPUT_RETRIEVED`), and the tenth is PGR. The last of those nine to remain merely ungraded, HSPA8, has since been searched on the exact question: across 7/7, 8/8 and 13/13 PubMed records on the *hsc70* promoter, hormone-response-element language, and their intersection, **not one maps an oestrogen, androgen, progesterone or glucocorticoid response element**, and the only cis-elements localised in a mammalian *hsc70* promoter are Sp1 sites (`research/modalities/hspa8-promoter-hormone-grade.json`).
>
> These are **retrieval negatives, not measured absences**, and both bounds are stated: 185 of 530 records were not open-access, and the HSPA8 result is an absence of asking — every study that dissected that promoter was asking about something else.
>
> #### 3. What survives: the imported input belongs to the partner
>
> Both routes fail, and they fail for reasons that share one structure. Across all twelve partners retrieved here, and across three tumour types, **the regulatory input a NR4A3 rearrangement imports is the 5′ partner's, never NR4A3's own**. Nine EMC partners contribute their own promoters; PGR contributes an oestrogen-driven promoter; GREB1 contributes a canonical oestrogen-receptor target promoter in uterine sarcoma; and in salivary acinic cell carcinoma the imported element is not a promoter at all but the SCPP secretory-protein enhancer at 4q13, juxtaposed to the NR4A3 transcription start site and up-regulating **wild-type** NR4A3 (`hormone-partner-lane.json`, `partners[]`). The breakpoint architecture is consistent with this in the one EMC case where a hormone-responsive partner was sequenced: the junction lies in NR4A3's 5′ UTR, upstream of coding sequence and downstream of NR4A3's own promoter.
>
> The claim's principal consequence is negative and it is the reason the claim is worth stating. NR4A3 is a MAPK-induced immediate-early gene, so the obvious idea — lower fusion transcription by inhibiting the signalling that drives NR4A3's own promoter — is **architecturally impossible**, because the fusion allele does not use that promoter. The same argument closes β-adrenergic, angiotensin-II and serum-response modulation of the fusion transcript. What this programme adds is that the argument no longer rests on a single case report: it now rests on twelve partners across three diseases, including one in which the imported element is an enhancer rather than a promoter.
>
> **We state plainly what kind of claim this is.** It is a structural argument built on retrieved, published rearrangement architecture and an annotation of the partner literature. It is **not** a measurement, and the one measurement we attempted did not corroborate it. A 5′-depletion signature — downstream junction coverage present while a gene's own 5′-most junctions carry none — was searched over the public splice-junction index (`research/modalities/emc-data-level-sweep.json`). The instrument answered: the absent control returned 0 records, the transport control returned 35,234, and both positive controls fired at the pre-registered operating point (ERG 252.0-fold enrichment, 191 candidates in 681 samples; FLI1 13.4-fold). **NR4A3 did not.** The regime tight enough to hold the background down left NR4A3 only 219 samples against the ~1,498 needed, yielding `TARGET_UNDERPOWERED_AT_THE_OPERATING_POINT`; and at the best-powered comparison available, over 34,013 samples, NR4A3 does not exceed the ordinary-gene envelope at any of 288 comparable cells (0.6722-fold, Katz 95% CI 0.6393–0.7068). That is an absent reading, and it is reported as one: it bounds this signature's reach over this index, and bounds nothing about the disease.
>
> ### Limitations
>
> This work has no wet laboratory and makes no efficacy, safety, selectivity, therapeutic-window or clinical-readiness claim for any agent, target or gene named; no compound named here is proposed as a treatment, and where a small molecule is mentioned it is a statement about reagent availability and its provenance. The dormancy-receptor result is an instrument limit on two specific archival array series and not a statement that the receptor is absent from EMC; both platforms map only 71% and 63% of their probes to symbols, so "no probe maps" is compatible with an unresolved identifier as well as with a genuinely absent probe. The dormancy-context elevation rests on a hand-curated, unpublished gene list, is uncorrected for multiple testing, and is a group-level abundance reading — abundance is not dependency, not protein, not activity, and not copy number. The reach bound rests on **zero events**, which bounds a rate without measuring one; the two cohorts are pooled under an **unverified assumption of non-overlap**, so 4.4% is the optimistic end of the honest range, and both cohorts genotyped with targeted assays that the single index case's own authors state would not have detected their fusion — so the true partner distribution could differ in either direction. The partner-map negatives are retrieval negatives bounded by 185 of 530 records whose full text was not open-access, and the promoter negatives are absences of asking rather than measured absences: no reporter assay was run, no promoter sequence was scanned against response-element matrices, and no receptor cistrome was read. The central architectural claim is a structural argument over published breakpoint architecture, not a measurement; its direct test in a public transcriptome index was underpowered and returned no signal above the ordinary-gene envelope; and its demonstrated scope is NR4A3 rearrangements in three tumour types, not fusion architecture in general. Three partners named in earlier internal lists (ACTB, CARMN, SLCO5A1) returned zero sources and are carried as unretrieved rather than as partners. Finally, one partner series (Paioli 2021) and the pazopanib trial's full partner distribution remain unretrieved behind subscription access, and their absence is recorded rather than worked around.

## Writability verdict

**WRITABLE NOW.**

Every number, identifier, quotation and negative in the drafted section already exists in the committed tree at HEAD `0d05cb7b`; nothing above required a retrieval, a run, or an input this repository does not hold. The paper is a **negative-results and fusion-architecture note**, not a perspective, and it is not the closed NR4A Perspective under another label: it grades two named routes against their own primary records, reports both as negative, and states one architectural claim with its evidence type on its face.

Three edits to the record must land with the writing, all of them corrections the record's own sources force:

1. `why_not_written` says the dormancy limit is one "no further expression work can close." **Narrow it to these two series.** The owning artifact's own next step is "a platform that carries the probe."
2. `what_it_would_claim` says the dormancy receptor "has the published tool compound this program's own receptor never had." **Narrow it.** No experimental structure, no measured binding constant; the repository's own artifact grades the capability-transfer premise REFUTED. Reagent-availability fact only.
3. `why_not_written` predates `research/modalities/hspa8-promoter-hormone-grade.json`. **Fold it in**: the last ungraded partner promoter is now graded, negatively, and the partner route has no remaining $0 step.

I hold **no write authority** on `systems/graph/publications.json` and made no edit; these are for the coordinator or the record's owner.

## Validation evidence

**RUN** (all in `/home/user/Rare-cancers`, read-only; `python3` = `/usr/local/bin/python3`; `git` read-only):

- `date -u; git rev-parse HEAD; git status --porcelain` — start (exit 0): `Tue Sep 8 05:10:21 UTC 2026`, `0d05cb7b…`, empty. End (exit 0): `Tue Sep 8 05:14:00 UTC 2026`, `997bc9e7…`, **0 lines**.
- Wilson recomputation, exit 0, verbatim output:
  ```
  58 0.062117855787202914
  26 0.1287289218592153
  84 0.04373172841465988
  ```
  Committed values in `hormone-partner-lane.json` → `reach`: `0.062117855787202914`, `0.1287289218592153`, `0.04373172841465988`. **Exact match, all three.**
- `python3 -c` reads of `emc-expression-panels.json` (exit 0): `NR2F1 in gene_reads: True`; both platform entries `"readable": false`, `"n_probes_mapping": 0`. NR4A3: `"readable": true`, `"n_probes_mapping": 1` on both.
- `python3 -c` read of `emc-data-level-sweep.json` (exit 0): `target_verdict = "TARGET_UNDERPOWERED_AT_THE_OPERATING_POINT"`, `controls_pass = true`, `absent_control_records = 0`, `positive_controls_that_fired = ["FLI1","ERG"]`, NR4A3 `n_pool = 219`, `n_candidates = 0`, `pool_that_would_be_needed = 1498`.
- Prior-work `rg`/`git ls-files` commands as quoted in *Prior-work check* (exit 0).
- Scratch cleanup: `rm -rf /tmp/claude-0/p6` then `ls -d /tmp/claude-0/p6` → `ls: cannot access '/tmp/claude-0/p6': No such file or directory`. **Scratch directory deleted.** (The composite command's exit 2 is that intended `ls` failure.)

**PROPOSED (NOT RUN):** no gate, test, linter, patch or repair was authored, proposed or applied. `scripts/preflight.sh` not run. `research/modalities/atr_hrd_sarcoma_series.py` not invoked in any form. No script was executed against repository data other than the read-only `json.load` inspections above.

**Not entered:** W25 scope — no `reports/W25-*`, no GSE243553, no continuation; `research/manuscripts/fusion-output/gse243553-eno3-overlap-2026-08-08.md` was listed by `ls` and deliberately not opened. No content-policy refusal occurred at any point.

## Limitations

(Scientific limitations of the paper are in the drafted Limitations paragraph above; these are limitations of **this verification**.)

I graded the repository's records against the repository's records. I retrieved nothing externally — no network is available and none was attempted — so every published count, quotation and identifier here is verified only to the point of *being faithfully transcribed within this tree*: I did not open PMID 36948401, PMC4015728, PMC9489176 or PMID 34812843, and cannot confirm the quoted sentences against their sources. Per the campaign's own measured finding, `verified: true`-style fields in this repository are unread by any executable and undecidable, so the provenance chain behind these counts is asserted by the artifacts and not independently corroborated by me. I checked one cohort-distribution owner (`nr4a3-emc-biology-evidence.md:29-31`) and not the full citation chain behind it. Agaram's 26 cases sum to 24 across the three named partners (16/7/1); the remaining 2 are unexplained in the line I read and I did not resolve them — it does not affect the zero-event count or the denominator, but it is an open loose end. I did not verify that the Huang and Agaram cohorts are non-overlapping, which the pooled bound assumes. The dormancy platform figures come from the committed derived panel; I did not re-read either raw series matrix, and one of them (GSE24369) is recorded elsewhere in this tree as having a retrieval-denied source matrix, so the derived reads are the only reachable form of that data here. I did not audit `hormone_partner_map.py`'s regex sweep and cannot say whether its 345-document enumeration missed a partner. Wall-clock and scope were deliberately bounded; this is a verification of two gradings and one claim, not a review of the whole programme.

## Tool-call and wall-clock count actually used

**29 tool calls** (all Bash; no Read/Write/Edit/Glob/Grep tool calls, no skills, no MCP, no network). **Wall clock ≈ 4 minutes of tool time** (05:10:21Z → 05:14:00Z) plus drafting. Both well inside the ~40/~40 target; early return.

## Next concrete action

**Write `research/manuscripts/occupancy/nr-outside-nr4a3.md` from the drafted section above**, as a preprint-target negative-results and architecture note, and flip `PUB-NR-OUTSIDE-NR4A3` from `outlined` to `drafted` with a `document.file` pointer — carrying the three record corrections named in the Writability verdict. Every input is on disk; the task is authorship, not retrieval. It needs a single named writer with write authority on `research/manuscripts/` and on the publication record, and it must not be split across workers: the three corrections and the draft are one coherent edit. Second-choice successor, if a writer cannot be seated: land the three record corrections alone, since the record currently over-states a live instrument limit as permanent and describes a partner-route step as open that has since been graded closed.
