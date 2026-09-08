<!-- collected 2026-09-08T05:19:29Z by campaign coordinator; agent id aaf579e7a8f0cc78a; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aaf579e7a8f0cc78a.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**P5**, PAPER lane, campaign OPUS-CAPACITY-CAMPAIGN-20260908. Candidate: `PUB-MATRIX-ADDRESS`.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

Start `date -u`: `Tue Sep  8 05:09:57 UTC 2026` · `git rev-parse HEAD` = `0d05cb7b3bf27921cceeb76bd69873ed89eb9fd6` · `git status --porcelain` = empty.
End `date -u`: `Tue Sep  8 05:12:52 UTC 2026` · `git rev-parse HEAD` = `997bc9e769da6bf606392941d46d20b319beab85` · `git status --porcelain` = empty. (HEAD advanced under me — coordinator commits, expected per COMMON-BRIEF §1. Every file I read is unchanged between the two: no working-tree write was made by me.)

Scratch directory `/tmp/claude-0/p5/` was created, never written into (all work was read-only inspection plus inline `python3 -c`), and **deleted** — `ls` confirms `No such file or directory`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`:

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy/truststore flags, no model name)
NO_PROXY=... (as above)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=... (as above)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

(The two long proxy/`no_proxy` values and `JAVA_TOOL_OPTIONS` are elided mid-line only where noted; they contain no model identifier. Nothing in this environment names a model.)

---

## Question

Do `PUB-MATRIX-ADDRESS`'s four route gradings hold against their own primary records, and does the distinction the paper turns on — **UNREACHABLE** versus **REFUTED** — survive verification well enough that the Results section can be drafted now?

It is open because the endpoint is `state: outlined` with **no `document` field and no manuscript file on disk**, while its `why_not_written` asserts a complete four-route grading and a specific contribution. Nobody has checked the assertion against the routes' own records, and no prose exists.

## Prior-work check

Commands run and what they showed:

- `rg -n -il "PUB-MATRIX-ADDRESS" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'` → 11 files: 6 generated `systems/views/*`, `systems/graph/routes.json`, `systems/graph/publications.json`, `research/manuscripts/REORG-PLAN.md`, `research/autonomy/research-ledger.json`. **No manuscript.**
- `git ls-files | rg -i "matrix|microenv|glycan|sulfat|immunocytokine|hypoxia"` → under `research/manuscripts/microenv/` there are exactly two files (`emc-hypoxia-reading.md`, `emc-hypoxia-map-edits.json`), neither of which is this paper. `research/manuscripts/REORG-PLAN.md:241` confirms `microenv/ — 2 files, Endpoints: PUB-MATRIX-ADDRESS`.
- `python3 -c` over `systems/graph/publications.json` → 33 endpoints; `PUB-MATRIX-ADDRESS` has no `document` key. `PUB-EMC-TISSUE-HYPOXIA`, proposed in `emc-hypoxia-map-edits.json` edit H2, **does not exist in the graph** — that proposal was never applied.
- `systems/views/paper-strength.md:79` → `| 26 | PUB-MATRIX-ADDRESS | ⛔ known negative / methods | — | 0.5 | 0 | 0 | ⚠ 4 | 50% of 8 | ◔ outlined |`.

**CLOSED-WORK.md confirmations.** I am not replaying: the rejected ICD-O registry paper; the clinical checkpoints; the NR4A Perspective refusal; the pazopanib/anthracycline/sunitinib/trabectedin/Wagner/CTARC unrecovered sources; GSE4303/GSE28866 rediscovery (I quote existing readings of GSE4303, and treat GSE28866 only as the memo's own named replication candidate, taking no new read). **Lane 2 is closed** — I make no `emc-expression-panels.json` arm-to-arm statistical claim of my own and restate no fibro/ECM `U`.

**W25 exclusion check, run deliberately.** `grep -l "GSE243553"` over my four primary sources returned only `systems/graph/routes.json`; a follow-up scan of that file shows the single occurrence sits in **`RT-FUSION-OUTPUT`**, not in any of my four routes. The fourth cohort here is `PRJNA1357027 / SRP640302`, a different deposit. **No expression read I use traces to held scope.** I read no `reports/W25-*`.

## Method and inputs

Read-only, live checkout at `/home/user/Rare-cancers` (HEAD as recorded above). No network, no paid API, no GPU, no CI dispatch, no `preflight.sh`, no `atr_hrd_sarcoma_series.py`. I did not use the frozen corpus: every path I cite resolves live, and per CORPUS-CONTEXT's W38b note the live tree is the correct tree for `:NN` citations.

| Input | Role |
|---|---|
| `systems/graph/publications.json` → `PUB-MATRIX-ADDRESS` | the endpoint record under audit |
| `systems/graph/routes.json` → `RT-MATRIX-SYNTHESIS`, `RT-MATRIX-ADDRESS`, `RT-IMMUNOCYTOKINE`, `RT-HYPOXIA-PRODRUG` | the four contributing routes and their `grade.value`/`grade.owner` |
| `research/modalities/census-route-expression-grading.json` | grade owner for three of four; per-gene figures and panel-group scores |
| `research/modalities/census_route_expression_grading.py` | the producer — establishes which parts are derived and which are hand-typed |
| `research/modalities/emc-expression-panels.json` | the artifact that **owns** every figure (`reads.read_2_CS_GAG_PAPS`, `reads.read_5_HYPOXIA`) |
| `research/manuscripts/microenv/emc-hypoxia-reading.md` §2.6, §2.7, §4, §5, §6, §7.1 | grade owner for the hypoxia route; the withdrawal's stated reason |
| `research/modalities/emc-fourth-cohort-route-readout.json` | per-route probe coverage in `PRJNA1357027`; the AUT-PD-116 adjudication rule |
| `research/manuscripts/microenv/emc-hypoxia-map-edits.json` | proposed-but-unapplied graph edits (provenance of the endpoint's framing) |
| `systems/views/paper-strength.md`, `research/manuscripts/REORG-PLAN.md` | endpoint standing and file inventory |

Two array series carry every expression figure below, quoted from `census-route-expression-grading.json → platforms`: **`GSE24369` on GPL6244 (6 EMC vs 29 comparator sarcomas)** and **`GSE4303-GPL3290` on GPL3290 (10 EMC vs 6 comparator)**. The artifact's own `_the_comparison_being_made` states: *"EMC tumour tissue against comparator sarcomas on the same array, expressed as a mean z difference. Magnitudes are NOT comparable across the two platforms; only sign agreement is."*

## Route-by-route grading verification (table)

Grade vocabulary as instructed. "Disposition asserted" is what `PUB-MATRIX-ADDRESS.why_not_written` claims; "verified?" is my finding against the route's own primary record.

| Route | What the route claimed | What was actually read | Repository path carrying it | Grade | Disposition asserted | Verified? |
|---|---|---|---|---|---|---|
| **RT-MATRIX-SYNTHESIS** — *"Inhibition of the tumour's glycosaminoglycan biosynthesis"* | Premise: *"CS biosynthetic and sulfation machinery HIGH in EMC"*; purpose *"Is the myxoid matrix load-bearing … such that stopping its manufacture is a therapeutic act?"* | Three panel groups on both platforms. **PAPS (sulfate-donor) module LOWER in EMC on both**: −0.3096 SD (t=−2.234, df=5.5, 5/5 genes readable) on GPL6244; −0.1616 SD (t=−2.113, df=13.6, 5/5) on GPL3290. **CS backbone polymerisation disagrees**: −0.1519 SD (t=−2.603, 6/6) vs **+**0.2933 SD (t=2.082, 5/6). **4-O-sulfotransferases disagree**: −0.0373 SD (t=−0.935, 4/4) vs +0.2145 SD (t=1.315, 4/4). Driver gene PAPSS2 Δ=−1.4241 / −0.8875. XYLT1 unreadable on GPL6244 (*"no probe … NOT a reading of absence"*). Every group verdict carries *"⚠ Uncorrected for multiple testing."* | `research/modalities/census-route-expression-grading.json` → `routes.RT-MATRIX-SYNTHESIS` (`observed`, `verdict`, `panel_groups`); grade copied to `systems/graph/routes.json` → `RT-MATRIX-SYNTHESIS.grade.value`; corroborated independently at `research/manuscripts/microenv/emc-hypoxia-reading.md` §4 (PAPS module t=−2.23/−2.11; PAPSS2 −3.94/−3.12; SLC35B3 −1.99/−6.37; CHST15 −6.90/−2.82; CHST11 flat +0.07/−0.50) | **ASSOCIATION** (group-mean z difference between arms in retrieved public array data; uncorrected, n_EMC = 6 and 10) | not-supported (as stated) | **YES** — and it is the only one of the four with a *concordant* negative on both platforms. The route's own `what_this_does_not_settle` limits it: the comparator arm is itself matrix-rich sarcoma, and *"bulk transcript of a biosynthetic enzyme need not track accumulated matrix mass in a tumour whose product is long-lived."* |
| **RT-MATRIX-ADDRESS** — *"Oncofetal chondroitin sulfate as a tumour address"* | Premise: the placental-type oncofetal CS **pattern** on EMC tissue; nominated proxy: 4-O-sulfotransferase arm **and** sulfate-donor module HIGH in EMC | **4-O arm discordant and significant on neither**, with all four genes (CHST11/12/13/14) readable on both platforms — a taken reading, not a missing one. CHST11 Δ +0.0064 / −0.2349; CHST12 +0.1307 / +0.3268; CHST13 −0.0719 / +0.4330; CHST14 −0.2142 / +0.3331. **Sulfate-donor module LOWER on both** (same PAPS figures as above — the panel's only concordant signal). Core proteoglycans mildly higher and significant on neither: +0.012 SD (t=0.309, 9/10) and +0.2552 SD (t=0.982, 9/10). | `research/modalities/census-route-expression-grading.json` → `routes.RT-MATRIX-ADDRESS`; `research/modalities/emc-expression-panels.json` → `reads.read_2_CS_GAG_PAPS` (`readability_verdict.state` = **PARTIALLY TAKEN**, 18 scored / 6 unscored units); `systems/graph/routes.json` → `RT-MATRIX-ADDRESS` | proxy read: **ASSOCIATION** (null); route's own premise: **UNSUPPORTED — no instrument exists in this corpus** | no-capacity-support | **YES.** The verdict field says it exactly: *"NOT SUPPORTED ON CAPACITY — AND THE ROUTE'S OWN QUESTION IS STILL UNREADABLE. This grades the proxy the route nominated, not the route's premise."* |
| **RT-IMMUNOCYTOKINE** — *"Matrix-targeted immunocytokines"* | Premise: a matrix epitope present in EMC stroma and restricted enough to address; direction needed: the epitope's parent genes present, ideally enriched | Three parent genes, all readable on both. **FN1 abundant but not enriched**: EMC array percentile **0.939** on GPL6244, Δ +0.0326; Δ +0.9733 on GPL3290 against a comparator arm at z=−1.18. **TNC LOWER on both**: Δ −0.2393 / −1.3534 (percentile 0.9546 / 0.3475). **FAP LOWER on both**: Δ −0.2652 / −0.1438. No panel-group score for this route. | `research/modalities/census-route-expression-grading.json` → `routes.RT-IMMUNOCYTOKINE`; `systems/graph/routes.json` → `RT-IMMUNOCYTOKINE.grade.value` | parent-gene read: **ASSOCIATION**; the route's actual address: **UNSUPPORTED — unreadable on this instrument** | present-but-not-selective, address is a splice variant a gene-level probe cannot see | **YES.** Verbatim: *"⛔ THE ADDRESS IS A SPLICE VARIANT, AND A GENE-LEVEL PROBE CANNOT SEE ONE."* One nuance the endpoint record loses: FN1 is not uniformly flat — it is flat on GPL6244 and +0.97 on GPL3290; the concordant negatives are TNC and FAP. |
| **RT-HYPOXIA-PRODRUG** — *"Hypoxia-activated prodrugs"* | Premise: a hypoxic fraction large enough to activate a prodrug; direction needed: hypoxia signature HIGH in EMC | **Raw contrast positive on both**: curated canonical HIF-target metagene +0.4168 SD (t=2.72, df=5.5, 15/15 readable) on GPL6244 and +0.9597 SD (t=4.882, df=10.7, 14/15) on GPL3290. **Then the audit.** Against a genome-wide size-matched null drawn from each platform's own mapped-symbol universe (2.3% and 3.1% signature membership, vs 33–34% for the earlier want-list null): **on GPL6244 not one of six signatures falls below 0.05** (Buffa 0.1055, Winter 0.0575, Harris 0.1875, Elvidge 0.077, HALLMARK 0.053, GO 0.0655); **on GPL3290 four of six do** (0.0315, 0.0415, 0.0165, 0.022). Leave-one-EMC-out: on GPL6244 **none** stays at \|t\| ≥ 2 across all six drops; on GPL3290 all six do. §2.6: the six signatures' per-sample scores correlate r = 0.66–0.95 / 0.73–0.96, so *"`all six positive` is one observation per platform, not six."* | Grade owner is **not** the census file — `systems/graph/routes.json` → `RT-HYPOXIA-PRODRUG.grade.owner` = `{file: research/manuscripts/microenv/emc-hypoxia-reading.md, anchor: 5--the-therapeutic-hooks-at-their-true-weight}`. Numbers at `emc-hypoxia-reading.md` §2.6–§2.7 and `research/modalities/emc-hypoxia-confounds.json`; reading state at `emc-expression-panels.json → reads.read_5_HYPOXIA` (**TAKEN**, 16/16 units scored) | **ASSOCIATION, WITHDRAWN as a grade** — the underlying contrast is a real measured association; what is withdrawn is what it licenses | WITHDRAWN same day | **Withdrawal verified; the "same day" timing is single-sourced — see below.** |

### The withdrawal record: located, quoted, dated — with one honest gap

The withdrawal is recorded in **two independent files**, and I found both.

1. `systems/graph/routes.json` → `RT-HYPOXIA-PRODRUG.grade.value`, verbatim:
   > *"⛔ GRADE WITHDRAWN AND REPLACED, 2026-08-09 (same day). It was first graded SUPPORTED from the raw two-platform contrast. That reading was taken from the panel artifact WITHOUT reading the confound audit that audits it: against a genome-wide size-matched null the signature does not clear on GPL6244, and the owning memo rules the signal is a reason to ask a question rather than to revisit this class."*

2. `research/modalities/census-route-expression-grading.json` → `routes.RT-HYPOXIA-PRODRUG.verdict`, verbatim:
   > *"⛔ WITHDRAWN — first graded SUPPORTED from the raw contrast; the confound audit restricts the signature to one of the two platforms and the memo that owns it declines to license this class from the signal at all."*
   and `route_action`: *"withdrawn; the owning memo's ruling stands and this grader defers to it."*

3. The same file carries the **cause**, as a top-level field named for it — `_a_grader_must_read_the_audit_not_only_the_reading`, verbatim:
   > *"⛔ ADDED AFTER THIS FILE GOT IT WRONG. emc-expression-panels.json holds READINGS; emc-hypoxia-confounds.json holds the AUDIT of one of them. Grading from the first without the second produced a SUPPORTED verdict on a signature its own genome-wide null restricts to one of the two platforms. An audit that reaches some consumers of a shared reading and not others is this repository's most-repeated failure, and here the grader WAS the consumer it did not reach. Any future grader over this panel must check whether a confound audit exists for the read it is using."*

4. The **ruling being deferred to** is `emc-hypoxia-reading.md` §5, dated `2026-08-07` in the document frontmatter, verbatim:
   > *"⛔ What this reading licenses: a hypothesis about tissue state that is worth putting into the literature because it is EMC-specific and measured, and that names three drug classes as things somebody could ask about. That is the entire licence."*
   > *"A hypoxia signature in EMC is therefore a reason to ask a question, not a reason to revisit that class — and any sentence that reads the other way is over-reading this memo."*

**The gap, reported as a finding rather than assumed away.** The **fact** and **reason** of withdrawal are doubly recorded and quotable. The **"2026-08-09 (same day)" timing is asserted in exactly one place** — the `routes.json` prose. `census-route-expression-grading.json` has **no generation-date field**, and its single occurrence of the string `2026-08-09` is in `_why` and refers to the *census registration* date, not to the grading or the withdrawal. `git log -- research/modalities/census-route-expression-grading.json` returns **one commit** (`14a3f172`) in this shallow clone, so the file's edit history is not reconstructible here. **The manuscript may state that the grade was withdrawn and why, citing both files; it may not state that the issue-and-withdrawal happened on the same day without attributing that specific claim to `routes.json`'s own prose.** The memo it defers to predates the grade by two days, which is consistent with, but does not establish, same-day withdrawal.

### One provenance caveat that must travel with all four rows

`research/modalities/census_route_expression_grading.py` separates cleanly: `gene()` at `:63` and `group()` at `:90` lift figures **verbatim** from `emc-expression-panels.json` (*"A scored group verdict as the panel emitted it, verbatim"*), and the module's `_this_artifact_computes_nothing_new` says *"Every figure is lifted from emc-expression-panels.json, which owns it."* But the `observed` and `verdict` **sentences are hand-typed prose inside that module**. The file itself records what that cost, in the sibling `RT-ALK-HIT` block: a hand-typed sentence contradicted the table directly above it, *"had already propagated by copy into systems/graph/routes.json's grade and into the generated route view"*, and was corrected only on **2026-08-29**. Numbers in this paper are derived and checkable; the four verdict sentences are editorial and one sentence in the same file was measurably wrong for three weeks. The manuscript should quote figures, not verdict prose.

## Unreachable versus refuted

This is the paper's contribution, so it needs stating in instrument terms rather than in outcome terms. **A route is REFUTED only if the instrument that was run is the instrument its premise names.** By that test the four split three ways, not two.

**RT-MATRIX-SYNTHESIS — REFUTED IN ITS STATED FORM; UNREACHABLE IN ITS RESTATED FORM.** The premise as written is about *biosynthetic enzyme transcript*, and enzyme transcript is precisely what a gene-level array measures. The instrument was correctly aimed, it fired, and it read against the direction the route needed on the one module that agrees across platforms. This is the paper's only genuine in-instrument negative. It is also the one whose restatement is unreachable: the route's own `remaining_unknowns` and the census `what_this_does_not_settle` both name the restatement — *matrix turnover*, not enzyme transcript — and no committed dataset supplies a turnover measurement. What would be needed: a pulse-labelled or isotope-turnover measurement of GAG synthesis and degradation in tumour tissue, or a quantitative measure of accumulated matrix mass per cell. Platform: not an array, not RNA-seq — a tissue or metabolic-labelling experiment. `routes.json` records the consequence honestly: `readiness.why_not_higher` = *"A contradicted premise with a plausible restatement is not yet a result in either direction."*

**RT-MATRIX-ADDRESS — UNREACHABLE.** The route's address is a **sulfation pattern**, and the corpus states the instrument fact in three independent places in the same words. `emc-expression-panels.json → reads.read_2_CS_GAG_PAPS.what_it_cannot_settle`: *"⛔ A SULFATION PATTERN HAS NO GENE. Transcript levels of sulfotransferases are a proxy for the CAPACITY to make an epitope, never a measurement of the epitope … only a stain or a binding assay can say that."* `emc-hypoxia-reading.md` §4 adds the mechanistic reason a capacity read cannot be inverted: *"Intracellular PAPS is set by flux and sulfate availability as much as by synthase transcript, so a low PAPSS2 read is not a measurement of low PAPS."* An epitope written slowly by a low-abundance enzyme onto a long-lived glycan is fully compatible with the observed negative capacity read. **For this route to be gradeable at all**, the measurable quantity would have to be the **glycan itself**: an antibody or lectin stain for the placental-type oncofetal CS epitope on EMC tissue, a recombinant VAR2CSA-type binding assay, or CS disaccharide compositional glycomics (4-O / 6-O / 4,6-O-disulfated CS-E ratios) by LC-MS/MS on digested tumour GAG. **Platform: tissue, wet bench.** There is no wet lab here. The correct reading is: *the capacity proxy the route itself nominated returned no support, and the route's premise was never tested by anything.* Reporting this as a negative result about oncofetal CS in EMC would be an error of exactly the kind the paper is about. `routes.json` says so in its own `readiness.missing`: *"a stain or a binding assay on EMC tissue — the epitope is a modification pattern and there is no further expression observation that could reach it."*

**RT-IMMUNOCYTOKINE — UNREACHABLE.** The clinical agents in this class bind an **oncofetal splice domain** of fibronectin or tenascin-C, not total FN1 or TNC protein, and the two array platforms quantify at gene level. `census-route-expression-grading.json`: *"its abundance is not deducible from the parent gene. So this reading bounds the parent genes and leaves the route's own premise untested."* **For this route to be gradeable**, the measurement would have to resolve **domain inclusion** — exon-level or junction-level quantification distinguishing the extra-domain-bearing transcript from the constitutive one. **Platform: transcript-resolved sequencing** (long-read, or short-read RNA-seq quantified at junction/exon level), or a domain-specific antibody stain on tissue. The corpus has already priced this and answered no, at $0, and the answer is unusually well documented. `routes.json → RT-IMMUNOCYTOKINE.required_validation[1]`, AUT-PD-116, 2026-09-02: the fourth cohort *"cannot resolve the oncofetal fibronectin and tenascin domains. TNC has no assigned probe at all; FN1 has exactly one across the 1,645 probes common to every run; gene counts are summed over the probes assigned to a gene … and the committed probe table carries `probe_sequence` and `assigned_gene` and no transcript or exon identity, so no domain-inclusion call is derivable from it."* `emc-fourth-cohort-route-readout.json → per_route.RT-IMMUNOCYTOKINE` confirms it row by row: `n_genes_named` 2, `n_genes_with_a_fourth_cohort_probe` 1 (FN1 true, TNC false). Three distinct instruments — two arrays and a targeted ligation panel — are all blind to the same thing, for the same structural reason.

**RT-HYPOXIA-PRODRUG — NEITHER.** It is **in-instrument and under-determined**, which is a third category the paper should not collapse into either of the other two. The signature is fully readable (`read_5_HYPOXIA` state **TAKEN**, 16/16 units scored, 15/15 and 14/15 genes readable), the contrast is positive on both platforms, and the audit that deflates it is itself a transcript-level instrument correctly applied. What the genome-wide null establishes is a **statement about statistical resolution on one of two series**, not about EMC biology: on the 6-tumour matrix-matched series the signature is not distinguishable from a random gene set of its size. The memo names the reachable falsifier and why it is unreached — §7.1: `GSE28866` (4 EMC vs 27 comparators, including **six myxoid liposarcomas**, a myxoid *and* fusion-driven comparator neither readable series contains) is blocked by *"a probe→symbol bridge, not data"*: GPL10999's probe-mapping rate is recorded as `None`. Verbatim: *"⛔ That is an instrument limit, not a biological null, and it is the same class of problem the GPL3290 EST-accession bridge already solved for GSE4303."* And the memo refuses to overstate: *"⚠ Nothing here says the bridge will resolve — GPL10999 was not attempted in this session and the honest state is 'unattempted', not 'solvable'."* Also non-negotiable for the draft: a hypoxia metagene is not an oxygen measurement, and §3 records that EWSR1::NR4A3's one published direct transactivation target here is **ENO3, a glycolytic enzyme** (PMID 26310886) — so a fusion driving glycolysis and a genuinely hypoxic tumour produce the same metagene score. (§2.7 F8 does bound this: removing every enolase leaves t = +3.30 / +5.74.)

**So the endpoint record's headline claim is verified, with one correction of emphasis.** Two of four are UNREACHABLE (`RT-MATRIX-ADDRESS`, `RT-IMMUNOCYTOKINE`), and they are unreachable for the same reason twice over: **the address is a post-transcriptional feature — a sulfation pattern, an alternatively spliced domain — and the field's cheap high-throughput instrument indexes genes.** A glycan has no gene; an isoform has a gene but shares it with the thing you are trying to exclude. The correction: the record calls the paper "mostly negative"; the more accurate summary is **one refuted premise, one withdrawn grade, and two routes that were never tested by anything** — and the *only* concordant cross-platform negative in the whole package is the sulfate-donor module, which does double duty in two of the four rows.

## Drafted section

Manuscript register. Every claim carries its source path. Each subsection leads with the negative or the instrument limit, not with the hypothesis. **No therapeutic handle, efficacy, selectivity, delivery or window claim appears anywhere below.** The word "handle" is used only as the name of a hypothesis that was graded.

---

### Results

We graded four proposed matrix-directed hypotheses in extraskeletal myxoid chondrosarcoma against the only expression data publicly readable for this disease: `GSE24369` on GPL6244 (6 EMC versus 29 comparator sarcomas) and `GSE4303` on GPL3290 (10 EMC versus 6 comparator), together with a targeted 12-tumour ligation panel (`PRJNA1357027`/`SRP640302`). Platform assignments and arm sizes are recorded in `research/modalities/census-route-expression-grading.json → platforms`. Because the two arrays differ in normalisation and comparator composition, magnitudes are not comparable across platforms and only sign agreement is interpreted; this rule is stated by the source artifact (`_the_comparison_being_made`) and is applied throughout. All group contrasts are uncorrected for multiple testing, and each verdict string in the source artifact carries that warning on its own face. Every figure below is lifted from `research/modalities/emc-expression-panels.json`, which owns it; no figure is re-derived here.

Two of the four hypotheses returned a reading against the direction they required. Two returned no reading at all, for a reason that is a property of the instrument rather than of the tumour. We report the second pair as unreached, not as negative, and the distinction is the substance of this section.

#### The tumour's sulfate-donor capacity reads lower than in comparator sarcomas, against the biosynthetic premise

The hypothesis that the defining matrix is a manufacturing dependency requires the biosynthetic and sulfation machinery to be elevated in EMC relative to comparators. It is not. The 3′-phosphoadenosine-5′-phosphosulfate (PAPS) module — the sulfate-donor arm on which every sulfation reaction depends — is **lower in EMC on both platforms**: −0.3096 SD units (t = −2.234, df = 5.5, n_EMC = 6, n_comparator = 29, 5/5 genes readable) on GPL6244, and −0.1616 SD units (t = −2.113, df = 13.6, n_EMC = 10, n_comparator = 6, 5/5 readable) on GPL3290 (`research/modalities/census-route-expression-grading.json → routes.RT-MATRIX-SYNTHESIS.panel_groups.paps_module`). The contrast is driven by PAPSS2 (Δ = −1.4241 and −0.8875). An independent audit of the same series reaches the same result gene by gene and adds the Golgi PAPS transporter SLC35B3 (t = −1.99, −6.37) (`research/manuscripts/microenv/emc-hypoxia-reading.md` §4).

The other two arms of the same panel do not agree between platforms and therefore support no call in either direction: chondroitin-sulfate backbone polymerisation reads −0.1519 SD (t = −2.603, 6/6 readable) on GPL6244 and +0.2933 SD (t = 2.082, 5/6) on GPL3290; the 4-*O*-sulfotransferase group reads −0.0373 SD (t = −0.935, 4/4) and +0.2145 SD (t = 1.315, 4/4). XYLT1 has no probe on GPL6244; the source artifact records this as *"no probe on this platform maps to the symbol; NOT a reading of absence."*

This is a relative statement, and its comparator is not a neutral one: the comparison arm is itself matrix-rich sarcoma. It is also a statement about transcript, and the source artifact states the limit that follows — bulk transcript of a biosynthetic enzyme need not track accumulated matrix mass in a tumour whose product is long-lived (`census-route-expression-grading.json → routes.RT-MATRIX-SYNTHESIS.what_this_does_not_settle`). The coherent reading of the whole panel is an abundant but comparatively **under-**sulfated matrix: the core proteoglycans sit at the top of the array (VCAN t = +3.94/+4.76, EMC array percentile 0.997/0.975; BGN +4.14/+3.87) while sulfate-donor capacity reads low, which is what a versican- and hyaluronan-dominated myxoid matrix — hyaluronan being unsulfated — would look like (`emc-hypoxia-reading.md` §4).

The premise as stated is not supported. The premise as it would have to be restated — a statement about matrix turnover rather than about enzyme transcript — is not addressed by any dataset available to us, and we do not report it as tested.

#### The oncofetal chondroitin-sulfate hypothesis was not tested, because a sulfation pattern has no gene

The proposed address here is a **glycan modification pattern**, and no transcript measurement can reach it. We state this before reporting any number, because the number that follows is a measurement of something else. The source artifact puts the limit in its own words: *"A SULFATION PATTERN HAS NO GENE. Transcript levels of sulfotransferases are a proxy for the CAPACITY to make an epitope, never a measurement of the epitope"* (`research/modalities/emc-expression-panels.json → reads.read_2_CS_GAG_PAPS.what_it_cannot_settle`).

What was measured is that capacity proxy, and it returned no support on either of its two arms. The 4-*O*-sulfotransferase arm that writes the pattern is discordant across platforms and significant on neither, with **all four genes readable on both platforms** — so this is a taken reading and not a missing one: CHST11 Δ = +0.0064 / −0.2349, CHST12 +0.1307 / +0.3268, CHST13 −0.0719 / +0.4330, CHST14 −0.2142 / +0.3331 (`census-route-expression-grading.json → routes.RT-MATRIX-ADDRESS.genes`). The sulfate-donor module is lower in EMC on both platforms, as reported above; it is the panel's only concordant signal, and it is the same observation that graded the biosynthetic hypothesis. The core proteins that would carry the chains are mildly higher on both and significant on neither (+0.012 SD, t = 0.309; +0.2552 SD, t = 0.982; 9/10 genes readable on each).

An unfavourable capacity read weakens this hypothesis and cannot close it. An epitope written by a low-abundance enzyme onto a long-lived glycan is entirely compatible with the reading above, and intracellular PAPS availability is set by flux and sulfate supply as much as by synthase transcript, so a low PAPSS2 value is not a measurement of low PAPS (`emc-hypoxia-reading.md` §4). Deciding this hypothesis requires a measurement of the glycan: a stain, a binding assay, or compositional glycomics on EMC tissue. None was performed, and the record states that this is the only remaining instrument (`systems/graph/routes.json → RT-MATRIX-ADDRESS.readiness.missing`). The twelve-tumour targeted panel does not help: of the three genes this hypothesis turns on, one has an assigned probe (CSPG4) and CHST11 and CHST3 have none (`research/modalities/emc-fourth-cohort-route-readout.json → per_route.RT-MATRIX-ADDRESS`). We report this hypothesis as **unreached**.

#### The matrix-directed antibody hypothesis was not tested either, because its address is a splice variant and every available probe is gene-level

The address proposed here is an oncofetal **splice domain** of fibronectin or tenascin-C. Three independent instruments in this study quantify at gene level, and a gene-level probe cannot distinguish a domain-bearing transcript from the constitutive one. The abundance of the isoform is not deducible from the parent gene (`census-route-expression-grading.json → routes.RT-IMMUNOCYTOKINE.what_this_does_not_settle`).

What the gene-level read does establish is a bound on the parent genes, and it is a mixed one. In absolute terms they are abundant: FN1 sits at the 94th percentile of its array on GPL6244 (EMC array percentile 0.939) and TNC at the 95th (0.9546). Relative to comparator sarcomas they are not enriched: FN1 is flat on GPL6244 (Δ = +0.0326) and higher on GPL3290 (Δ = +0.9733, against a comparator arm at mean z = −1.18); TNC is lower on both (Δ = −0.2393, −1.3534); FAP is lower on both (Δ = −0.2652, −0.1438) (`census-route-expression-grading.json → routes.RT-IMMUNOCYTOKINE.genes`). Present, and not selective against other sarcomas — but selective against what an agent of this class would need is a question about the isoform, which is not what was measured.

Whether the targeted twelve-tumour panel could resolve the isoform was asked directly and answered no, at no cost. TNC has no assigned probe at all; FN1 has exactly one across the 1,645 probes common to every run; gene counts are summed over the probes assigned to a gene; and the committed probe table carries probe sequence and assigned gene and **no transcript or exon identity**, so no domain-inclusion call is derivable from it (`systems/graph/routes.json → RT-IMMUNOCYTOKINE.required_validation[1]`, adjudicated 2026-09-02; per-gene coverage at `research/modalities/emc-fourth-cohort-route-readout.json → per_route.RT-IMMUNOCYTOKINE`). Resolving this hypothesis requires transcript-resolved sequencing quantified at junction or exon level, or a domain-specific stain. We report it as **unreached**.

#### The hypoxia grade was issued and withdrawn, and the audit that withdrew it is the result

The raw contrast is positive and reproducible in sign. A curated canonical HIF-target metagene scores higher in EMC than in comparator sarcomas on both platforms: +0.4168 SD units (t = 2.72, df = 5.5, 15/15 genes readable) on GPL6244 and +0.9597 SD units (t = 4.882, df = 10.7, 14/15 readable) on GPL3290 (`census-route-expression-grading.json → routes.RT-HYPOXIA-PRODRUG.panel_groups`).

That reading was first graded as supporting the hypothesis, and the grade was **withdrawn and replaced** once the confound audit of the same reading was consulted (`systems/graph/routes.json → RT-HYPOXIA-PRODRUG.grade.value`, which states the withdrawal, its cause and the date 2026-08-09; independently recorded at `census-route-expression-grading.json → routes.RT-HYPOXIA-PRODRUG.verdict` and `.route_action`). The stated cause is worth reporting in full, because it is a failure mode of shared-artifact reasoning rather than of statistics: *"emc-expression-panels.json holds READINGS; emc-hypoxia-confounds.json holds the AUDIT of one of them. Grading from the first without the second produced a SUPPORTED verdict on a signature its own genome-wide null restricts to one of the two platforms"* (`census-route-expression-grading.json → _a_grader_must_read_the_audit_not_only_the_reading`).

Two audit results carry the withdrawal. First, multiplicity: six published hypoxia signatures with genuinely distinct membership (pairwise Jaccard 0.04–0.28; 546 genes in the union, 377 in exactly one set) have per-sample scores that correlate r = 0.66–0.95 on GPL6244 and 0.73–0.96 on GPL3290, so "all six positive" is **one observation per platform, not six** (`research/manuscripts/microenv/emc-hypoxia-reading.md` §2.6). Second, and decisively, a genome-wide size-matched null drawn from each platform's own mapped-symbol universe: on GPL6244 **not one** of the six signatures reaches p < 0.05 (0.1055, 0.0575, 0.1875, 0.077, 0.053, 0.0655), while on GPL3290 four of six do (0.0315, 0.0415, 0.0165, 0.022) (§2.7). Leave-one-tumour-out is concordant with that split: on GPL6244 no signature holds |t| ≥ 2 across all six drops, on GPL3290 all six do.

The two available nulls disagree, and the memo that owns the audit treats the disagreement as informative rather than as a defect: label permutation asks whether these arms separate on this score, the random-set null asks whether this set is special among sets of its size, and a signature can pass the first and fail the second when the arms differ on a broad axis that many gene sets partly report (§2.7). A confound the transcript instrument cannot separate remains open on the other side: the fusion's one published direct transactivation target in this disease is the glycolytic enzyme ENO3 (PMID 26310886), and a fusion driving glycolysis and a genuinely hypoxic tumour produce the same metagene score (§3) — bounded, but not eliminated, by the observation that removing every enolase leaves t = +3.30 / +5.74 (§6, F8).

The falsifier is named and is not exhausted: a third EMC series. The candidate is identified — `GSE28866`, whose comparator arm carries six myxoid liposarcomas, a myxoid and fusion-driven comparator neither readable series contains — and what blocks it is a probe-to-symbol bridge on GPL10999 rather than absent data. The memo is explicit that this is an instrument limit and not a biological null, and equally explicit that the bridge was never attempted, so the honest state is unattempted rather than solvable (§7.1). Of the eight genes this hypothesis turns on, only VEGFA has an assigned probe in the twelve-tumour panel (`emc-fourth-cohort-route-readout.json → per_route.RT-HYPOXIA-PRODRUG`).

We therefore report no grade for this hypothesis. The measured signal stands as a description of tissue state on one of two series; it licenses a question, and the memo that owns the audit declines to license anything further from it (`emc-hypoxia-reading.md` §5).

#### The pattern across the four

Only one of the four hypotheses was decided by the instrument that its own premise names, and it was decided against. One was issued a grade and had it withdrawn on audit. The remaining two were never tested: in both, the proposed address is a post-transcriptional feature — a sulfation pattern in one case, an alternatively spliced domain in the other — and the high-throughput instruments available for a disease this rare index genes. A glycan modification has no gene. An isoform has a gene, and shares it with precisely the species one is trying to exclude. That both hypotheses failed to be gradeable for the same structural reason, on three independent platforms, is the finding we regard as generalising beyond this tumour.

---

### Limitations

This study measured transcript in archival tumour tissue and nothing else. Every statement above is a statement about RNA abundance; none is a statement about protein level, protein localisation, enzymatic activity, copy number, glycan structure, oxygen tension or matrix mass. **No claim is made or implied here about the activity, selectivity, safety, therapeutic window, deliverability or clinical readiness of any agent or agent class in this disease.** The three "handles" named in the framing of this work are hypotheses that were graded, and two of them were not gradeable.

The evidence base is small and its arms are not matched. Sixteen tumours across two array series, on decade-old platforms, with comparator arms that differ in both size and composition — 6 EMC against 29 comparators on GPL6244, 10 against 6 on GPL3290 — and a twelve-tumour targeted panel whose gene space is the panel's rather than the transcriptome's, in a single sequencing batch of FFPE material collected between 1997 and 2020, split by the depositors' own unexplained prognostic key. No differential-expression result is available or computed at that design (`research/modalities/emc-fourth-cohort-route-readout.json → cohort`). All group contrasts are uncorrected for multiple testing. Magnitudes are not comparable across the two array platforms; only sign agreement is interpreted, and where the two platforms disagree we report no call rather than the more favourable one.

The comparator is not normal tissue. Every "not enriched" and "lower in EMC" statement above is relative to other sarcomas, several of them matrix-rich, and none of these readings speaks to the contrast against normal tissue that any addressing question would ultimately turn on.

Two hypotheses are reported as unreached, and we intend that to be read strictly: unreached is not a negative result, and nothing above should be cited as evidence against oncofetal chondroitin-sulfate or against oncofetal fibronectin/tenascin domains in this disease. Deciding either requires an instrument we did not have — a stain, a binding assay or compositional glycomics for the first; transcript-resolved sequencing at exon or junction level, or a domain-specific stain, for the second. There is no laboratory associated with this work, and no experiment was performed.

The withdrawn hypoxia grade is reported with its audit rather than its headline, and the audit itself has limits. A hypoxia metagene is a transcriptional shadow of hypoxia: no oxygen was measured and no hypoxia marker was stained. The signature cannot separate tumour-cell hypoxia from a hypovascular matrix compartment, and it cannot separate hypoxia-driven from fusion-driven glycolytic transcription. Necrosis was not directly testable from transcript; the available myeloid proxy points away from it, and that is the most this instrument can say. The named falsifier — a third independent series — remains open, and the candidate series is blocked by an unattempted probe-annotation bridge whose resolvability is unknown.

Finally, a provenance limit on the sources themselves. The figures quoted here are derived and are owned by `research/modalities/emc-expression-panels.json`; the verdict sentences in `research/modalities/census-route-expression-grading.json` are hand-written summaries within that module, and that module records an instance in which such a sentence contradicted the table above it and propagated into two downstream files before correction. We have quoted figures rather than verdict prose wherever the two could differ. The assertion that the hypoxia grade was withdrawn on the same day it was issued rests on a single prose field in `systems/graph/routes.json`; the withdrawal itself is independently recorded in two files, its timing is not.

---

## Writability verdict

**WRITABLE NOW.**

Every claim in the drafted section resolves to a committed path in this checkout, and I verified each of the four gradings against the record that owns it. The endpoint needs three changes that are editorial rather than evidentiary, and the draft above already makes all three:

1. **The title must change.** *"The myxoid matrix as an address rather than an obstacle"* asserts the conclusion the work did not reach. The paper's actual result is about instrument reach. A title in the shape of *"Three matrix-directed hypotheses in extraskeletal myxoid chondrosarcoma: one refuted, one withdrawn on audit, and two addresses that no available instrument can see"* matches what the evidence supports.
2. **`what_it_would_claim` must be restated.** As written it says the matrix *"admits at least three distinct handles"*; the graded record says two of those were never tested and one was refuted as stated. The current claim field would fail its own evidence.
3. **The blocker attribution is stale.** `PUB-MATRIX-ADDRESS.blocked_by` is `["BLK-NO-EMC-DATA"]`, and its own `why_not_written` opens *"ITS BLOCKER IS NOW RETIRED"*. Under the AUT-PD-116 rule (`emc-fourth-cohort-route-readout.json → "⭐ the_rule_this_adjudication_applies"`), `BLK-NO-EMC-DATA` covers a requirement only if an EMC **functional-genomics** dataset would satisfy it; the residuals on the two unreachable routes are a bench (`BLK-NO-WET-LAB`), which the two routes already carry individually. This is a graph edit, it is the coordinator's or the owner's to make, and it is **not** a precondition for drafting.

Nothing in the draft requires a new measurement, a fetch, a CI run, or a wet lab. What the paper would need before *posting* — as distinct from writing — is a human read on point 1 and 2, and a decision by the owner, since publication authority is not mine and I published nothing.

## Validation evidence

**RUN.** Environment: `/home/user/Rare-cancers`, Linux container, `python3` = `/usr/local/bin/python3`, `CLAUDE_CODE_VERSION=2.1.42`. No network egress attempted, no paid API, no GPU, no CI dispatch. `scripts/preflight.sh` not run (dispatch forbids it). `research/modalities/atr_hrd_sarcoma_series.py` not invoked in any form.

| Command | Result |
|---|---|
| `date -u; git rev-parse HEAD; git status --porcelain` (start) | `Tue Sep 8 05:09:57 UTC 2026`; `0d05cb7b3bf27921cceeb76bd69873ed89eb9fd6`; empty. exit 0 |
| `env \| grep -i -E 'claude\|anthropic\|model' \| sed -E ...` | output pasted verbatim under **Worker**. exit 0 |
| `cat` / `Read` of `COMMON-BRIEF.md` (816 lines, read in two pages), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md` | all three read in full. exit 0 |
| `python3 -c "…json.load('systems/graph/publications.json')…"` | list of 33 records; `PUB-MATRIX-ADDRESS` printed in full; no `document` key. exit 0 |
| `python3 -c "…routes.json … 'PUB-MATRIX-ADDRESS' in json.dumps(r)…"` | exactly 4 routes returned: `RT-MATRIX-SYNTHESIS`, `RT-MATRIX-ADDRESS`, `RT-IMMUNOCYTOKINE`, `RT-HYPOXIA-PRODRUG`. exit 0 |
| `python3 -c "…census-route-expression-grading.json … routes[k]…"` for the four ids | all figures in the grading table above printed verbatim. `summary` = supported 2, against 3, **withdrawn 1** (`RT-HYPOXIA-PRODRUG`), split_or_unread 10. exit 0 |
| `sed -n '148,230p'` and `'284,400p'` and `'400,470p'` of `emc-hypoxia-reading.md` | §2.6, §2.7, §4, §5, §6, §7.1 read; all quoted numbers taken from these lines. exit 0 |
| `python3 -c "…emc-fourth-cohort-route-readout.json…"` | `per_route` for all four; `cohort` = `PRJNA1357027`/`SRP640302`, 12 runs, 862 genes with ≥1 assigned probe, 1,645 probes offered, `gene_counts_sha256` == `gene_counts_recomputed_sha256` = `8aa3064a…`. exit 0 |
| `grep -l "GSE243553"` over my 4 primary sources | only `systems/graph/routes.json`; follow-up scan shows the sole carrier is `RT-FUSION-OUTPUT`. **W25-held scope is absent from all four routes.** exit 0 |
| `rg -n -il "PUB-MATRIX-ADDRESS" …`, `git ls-files \| rg -i …` | prior-work results as reported above. exit 0 |
| `grep -n "def \|observed\|verdict" research/modalities/census_route_expression_grading.py` | `gene():63`, `group():90` (*"as the panel emitted it, verbatim"*); `observed`/`verdict` are module-level string literals; the `:235` self-correction record read. exit 0 |
| `git log --oneline -3 -- research/modalities/census-route-expression-grading.json` | one commit (`14a3f172`) — shallow clone, history not reconstructible. This is the basis for the single-sourced-date finding. exit 0 |
| `rm -rf /tmp/claude-0/p5; ls -d /tmp/claude-0/p5` | `No such file or directory` — scratch deleted. exit 0 (from `date`) |
| `date -u; git rev-parse HEAD; git status --porcelain` (end) | `Tue Sep 8 05:12:52 UTC 2026`; `997bc9e769da6bf606392941d46d20b319beab85`; **empty**. exit 0 |

**PROPOSED (NOT RUN).** The Results and Limitations text above is a **draft returned in this report**, not a file. No manuscript was written, no graph field edited, no view regenerated, no gate run, no test authored, no patch proposed. The three endpoint edits named under **Writability verdict** are proposals for the owner and were not applied.

**Content-policy refusals: none encountered.**

## Limitations

This is a **verification of gradings against committed records**, not an independent re-analysis. I did not recompute a single t-statistic, z-difference or null fraction; I checked that each grade's assertion matches the artifact that owns it, and that the artifact's own caveats are carried forward. If `emc-expression-panels.json` is wrong, everything above inherits that error, and Lane 2's closure notes give a live reason for caution about *statistical* claims on that substrate (a measured gene-set-independent offset between the EMC arm's six GPL6244 arrays and comparator arrays, with batch, scan date, processing and cellularity all confounded with disease class and none separable). I make no arm-to-arm statistical claim of my own, and the draft above reports platform disagreement as no-call throughout, which is the conservative direction under that caution.

The `same day` timing of the hypoxia withdrawal is single-sourced and, in this shallow clone, not checkable. I report it as an attributed quotation, not as an established fact.

I did not read `research/modalities/emc-hypoxia-confounds.json` (189 KB) directly; the §2.7 figures are quoted from the memo that derives them, which is the memo's stated relationship to that artifact. A referee-grade check would confirm the six null fractions against the JSON.

I did not audit the `GSE28866`/GPL10999 bridge claim beyond the memo's own words, and the memo itself says the bridge is unattempted rather than solvable. Whether a third series is obtainable is **UNKNOWN**, and no retrieval was attempted (none is authorised here).

This report cannot say whether the paper *should* be posted. Publication authority is not mine, `publish_bar.py` was not run, and nothing was published, submitted or transmitted anywhere.

## Stop condition

**Set:** stop when (a) all four gradings are checked against their own primary records with paths and figures, (b) the withdrawal record is either located and quoted or reported as unlocatable, (c) the UNREACHABLE/REFUTED split is stated in instrument terms for all four, (d) a Results and Limitations draft exists in this report, and (e) a writability verdict is stated — **or** when a W25-held dependency blocks a route, in which case that route stops and is reported blocked.

**Met.** All five conditions satisfied; the W25 branch condition did not fire — the exclusion check returned clean, with the single `GSE243553` reference in `routes.json` confined to `RT-FUSION-OUTPUT`, outside this paper's four routes. Returned early against the ~40-call / ~40-minute target.

## Tool-call and wall-clock count actually used

**20 tool calls. 2 minutes 55 seconds wall clock** (05:09:57Z → 05:12:52Z). Both well inside the ~40/~40 target; early return, per the brief.

## Next concrete action

**One task, for the paper lane, for the coordinator or the endpoint owner to route:** take the Results and Limitations text in this report, place it at `research/manuscripts/microenv/emc-matrix-address-grading.md` with the standard frontmatter, add the missing sections (Introduction, a Methods section that names the two series, their arm sizes, the panel-group construction and the "sign agreement only" rule, and a Discussion that argues the glycan/isoform instrument gap as the generalising claim), and in the same commit make the three endpoint edits named above: retitle, restate `what_it_would_claim` to match the graded record, move `PUB-MATRIX-ADDRESS.state` from `outlined` to `drafted` with a `document.file` pointer, and correct `blocked_by` under the AUT-PD-116 rule. That is a single writer's task, needs no new measurement and no new data, and it converts the campaign's only fully-graded, fully-sourced, entirely unwritten endpoint into a draft.

**Do not** pair it with an attempt on the GPL10999 bridge. That is a separate, differently-authorised task, its outcome is genuinely unknown, and the paper above is complete and honest without it — the third series is named as the open falsifier, which is the correct way for a negative-and-instrument-limits report to leave it.
