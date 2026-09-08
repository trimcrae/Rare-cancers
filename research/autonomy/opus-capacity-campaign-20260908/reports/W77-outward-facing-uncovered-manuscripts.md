<!-- collected 2026-09-08T05:06:36Z by campaign coordinator; agent id a89e0464ae07cfa37; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a89e0464ae07cfa37.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

W77, campaign OPUS-CAPACITY-CAMPAIGN-20260908, lane: preflight-gate audit (W59's named successor).

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at **start** (identical at end; re-checked keys `AI_AGENT`, `CLAUDE_EFFORT`, `CLAUDE_CODE_VERSION`, `ANTHROPIC_BASE_URL`):

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
GLOBAL_AGENT_NO_PROXY=<same no_proxy list>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 … (proxy/truststore flags)
NO_PROXY=<same list>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same list>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**State.** Start `date -u` = `Tue Sep  8 04:56:38 UTC 2026`, HEAD `129a4e2a1c39352a7a697c42445bb27fc50f9b0c`, `git status --porcelain` **empty**. End `date -u` = `Tue Sep  8 05:00:59 UTC 2026`, HEAD `49ed4d4e94df6753a7300b893d718583f87a03e3`, `git status --porcelain` **empty**. HEAD advanced by coordinator commits during the run (expected, COMMON-BRIEF §1); I ran no git write operation and wrote nothing under `/home/user/Rare-cancers`. Scratch `/tmp/claude-0/w77/` deleted (`rm -rf`; `ls /tmp/claude-0/` no longer lists `w77`).

## Question

W59 measured that citation identifiers are gated over 187/187 manuscripts by discovery while claim strength, style register, submission residue and numeric conformance are gated over 41/187 by enumeration. Which of the uncovered manuscripts are **internal working record** (correctly outside a submission gate) and which are **outward-facing** (a submission text, a deposited payload file, a cover letter, an SI — able to leave the building while linted only for citation identifiers)? Cross the uncovered set against `systems/graph/publications.json` (`document.file`, `state`, `level`), `research/manuscripts/submission-metrics.json`, `research/manuscripts/build_submission_pdf.PAPERS`, and the deposited/archive manifests.

## Prior-work check

- Read in full, as instructed, before doing anything: `COMMON-BRIEF.md` (601 lines), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W59-manuscript-linter-coverage.md`, `reports/W51-lint-consistency-coverage.md`. W59's, W51's, W64's and W47's results are taken as given; I re-derived only the file sets I needed as *inputs* to the classification, not to re-measure their coverage claims (and the re-derivation reproduced every per-gate number exactly — see the one arithmetic discrepancy below, which I did not go looking for).
- `reports/W25-*` not read, not referenced. PUB-ASO documents were read read-only (frontmatter and headers only) and not edited.
- No repository search for novelty was needed: the question is a cross-product of four named artifacts, not a claim of novelty. The four closed-work items adjacent to this lane (the ASO submission and Qeios history are owned by the submission owner; the frozen external-validation comment; the rejected ICD-O classification paper; the blocked NR4A Perspective) were checked against my output lists — none is classified or touched here, and classifying a document's *role* is explicitly not an authorisation to send it anywhere.

## Method and inputs

Live checkout `/home/user/Rare-cancers` at HEAD `129a4e2` → `49ed4d4`. No corpus read was needed (this question is about the live tree's current state). `/usr/local/bin/python3` (3.11), stdlib only. Every Python invocation ran with `PYTHONDONTWRITEBYTECODE=1` so no `__pycache__` was written into the tree (W59's honest deviation, avoided).

1. **Denominator**: `git ls-files 'research/manuscripts/*' | grep '\.md$'` → **187**, identical to W51's and W59's.
2. **Covered set**: imported `lint_claims.DEFAULT_TARGETS`, `lint_style.TARGETS`, `lint_submission_residue.targets()`, and walked `research/manuscripts/pinned-figures.json` for `targets` / `must_appear_in` / `file` (the `lint_consistency` set). Reproduced per-gate: **claims 36, style 13, residue 34, consistency 16** — all four match W59/W51 exactly.
3. **Cross-product evidence**, one signal per artifact:
   - `systems/graph/publications.json` — `document.file`, `state`, `level`, `target_venue`, `posted`.
   - `research/manuscripts/submission-metrics.json` `rows[].file` + `rows[].companion_files[]` (5 rows → 7 files).
   - `research/manuscripts/build_submission_pdf.py` — `PAPERS` (5 `.md`) **and** `STAMP_SOURCES` (`:2261-2266`), which `PAPERS` alone misses.
   - `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` — the deposited payload (516 files, `deposition_doi 10.5281/zenodo.22229096`), and its `promises[]` block, which states *why* each file is deposited.
   - Secondary channel sweep over the 11 tracked outward-channel artifacts (`*aixiv-metadata*`, `deposit-state.json`, `zenodo_deposit.py`, `build_submission_{pdf,docx,parts}.py`, `print-formats-manifest.json`, the archive manifest).
4. **Document self-declaration**: parsed YAML frontmatter (`kind`, `status`, `title`, `audience`, `purpose`, `scope`) for every uncovered file, then read the header of each ambiguous candidate.

## Result

### Correction to W59's union arithmetic (PRIMARY, measured)

W59's four per-gate counts reproduce exactly (36 / 13 / 34 / 16), but their **union is 42, not 41**, so the uncovered set is **145, not 146**. I did not seek this; it fell out of building the list. W59's substantive finding is unaffected (21.9% → 22.5%; 78.1% → 77.5%). The 42 covered files and their gate memberships were enumerated in full; the discrepancy is in the union step alone, and I cannot reconstruct which file W59 dropped.

### The decisive negative: `publications.json` is not the leak (PRIMARY)

All **26** `publications.json` entries carrying a `document.file` are **covered** — **0 of 26 are in the uncovered set**. Seven further entries (`PUB-CARE-DELIVERY`, `PUB-IPD-SURVIVAL`, `PUB-KINASE-LEADS`, `PUB-LOCOREGIONAL`, `PUB-MATRIX-ADDRESS`, `PUB-NR-OUTSIDE-NR4A3`, `PUB-PARKED-MODALITIES`) are `unwritten`/`outlined` with `document: None`, so they name no file. Every uncovered file likewise scored `submission_metrics: False` and `build_pdf: False` against `PAPERS`. **The model-driven half of the gate does its job completely**: anything the graph calls a publication endpoint is linted. The entire gap consists of documents the graph does not model as endpoints.

### Classification — 16 OUTWARD-FACING / 3 UNKNOWN / 126 INTERNAL WORKING RECORD (n = 145)

#### OUTWARD-FACING — 16

**Group 1 · Deposited payload files (6) — hard evidence, strongest rows.** Each is a member of `fusion-junction-aso-archive-manifest.json` `files[]` (deposited under DOI `10.5281/zenodo.22229096`) and is named in a `promises[]` entry that records the reader-facing promise it discharges. All six are in `lint_citations` only.

| File | Evidence |
|---|---|
| `research/manuscripts/aso/fusion-junction-aso-submission-tables.md` | manifest member; `build_submission_pdf.py:2263` `STAMP_SOURCES`; promise `per_design_tables`; and `build_submission_pdf.py:429-437` states in-source that *"the availability statement names `fusion-junction-aso-submission-tables.md` as the machine-readable copy of Tables 1 to 7, and it IS in the deposit — so it is the one .md filename a reader may correctly be sent to"* |
| `research/manuscripts/aso/fusion-junction-aso-submission-references.md` | manifest member; `build_submission_pdf.py:2264` `STAMP_SOURCES`; promise `retrieval_records` |
| `research/manuscripts/aso/fusion-junction-aso-references.md` | manifest member; promise `retrieval_records`; frontmatter `kind: generated`, title *"References — fusion-junction ASO manuscript"* |
| `research/manuscripts/aso/aso-citations-priorart-2026-08-08.md` | manifest member; promise `retrieval_records` — *"the retrieval records for every literature claim"* |
| `research/manuscripts/aso/aso-delivery-antigen-2026-08-08.md` | manifest member; promise `delivery_antigen_negative` (the deposited negative finding) |
| `research/manuscripts/aso/fusion-junction-aso-paper-redteam.md` | manifest member; promise `correction_record` — *"The complete correction record, including every superseded value"*. ⚠ **Shape/role conflict worth a human eye**: by shape this is a red-team round, i.e. exactly the class `lint_style`'s own scoping rationale says must not be added ("a memo, a plan or a findings note must not be added here"); by evidence it is a deposited payload the paper promises to readers. Its sibling `fusion-junction-aso-working-record.md`, deposited under the *same* promise, **is** covered (by `lint_claims`) |

**Group 2 · Ready-to-send correspondence (7) — self-declared in frontmatter `purpose`.** Five cover letters share the same purpose formula, *"Hold the ready-to-send cover letter accompanying `<paper>` to `<named journal>`, with the fit statement, the scope disclosure, the preprint note…"*:

- `research/manuscripts/dependency/emc-atr-collaborator-package-cover-letter.md` → Genes, Chromosomes and Cancer
- `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-cover-letter.md` → Genes, Chromosomes & Cancer
- `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis-cover-letter.md` → Genes, Chromosomes and Cancer
- `research/manuscripts/repurposing/repurposing-hypotheses-cover-letter.md` → Critical Reviews in Oncology/Hematology
- `research/manuscripts/surface-targets/emc-surface-target-landscape-cover-letter.md` → British Journal of Cancer
- `research/manuscripts/surface-targets/emc-surface-target-outreach.md` — title *"Outreach emails — EMC surface-target preprint → the patient-derived-EMC-model groups"*. ⭐ **Direct inconsistency evidence**: its exact counterpart `research/manuscripts/degrader/nr4a3-degrader-outreach-emails.md` **is** covered (by `lint_claims`). Two outreach-email documents, one gated, one not.
- `research/manuscripts/degrader/nr4a3-degrader-ncs-presubmission-inquiry.md` — title *"NCS presubmission inquiry — draft (the free long shot)"*; `status: live`. A draft, but a draft **of** correspondence to a journal.

⚠ Note the asymmetry inside PUB-ASO: `fusion-junction-aso-cover-letter.md` **is** covered (by `lint_consistency`, via `pinned-figures.json` `must_appear_in`). Five sibling cover letters of the same formula are not — coverage here is a by-product of a pinned *number* happening to live in that one letter, not of it being a cover letter.

**Group 3 · Standalone live manuscripts the graph does not model (3).** Paper-titled, `status: live`, no supersession banner, not a `publications.json` endpoint, in no submission-format build:

- `research/manuscripts/endpoint/meta-analysis.md` — *"Pooled outcomes of extraskeletal myxoid chondrosarcoma: a reproducible systematic review and meta-analysis"*; body banner: *"SEPARATE-TRACK MANUSCRIPT (EMC outcomes, not treatment). A distinct paper on prognosis built on the patient registry."* This is the manuscript side of the pooler W53 audited.
- `research/manuscripts/fusion-direct/fusion-coactivator-ppi-paper.md` — banner *"CONCEPT / IN-SILICO POSITIONING PAPER"*
- `research/manuscripts/fusion-direct/fusion-condensate-disruption-paper.md` — banner *"IN-SILICO / CONCEPT PAPER"*

#### UNKNOWN — 3 (genuinely ambiguous; not guessed either way)

| File | Why UNKNOWN |
|---|---|
| `research/manuscripts/fusion-direct/fet-fusion-trial-eligibility-notice.md` | **Hybrid, and the highest-stakes row.** `kind: memo`, but its own `purpose` says it *"carries the draft paragraph and the reviewer block it must pass through before it goes anywhere"*, and its `scope` says *"the notice it carries in section 4 is an UNPUBLISHED DRAFT awaiting the review in section 5, and the two must not be confused… NOTHING HERE HAS BEEN SENT, PUBLISHED OR SHOWN TO"* (truncated at my read boundary). The container is an internal record; the payload is **patient/clinician-facing** text. Whether the containing file is inside a submission gate is a scoping decision, not a measurement |
| `research/manuscripts/neoantigen/clinical-brief-emc-neoantigen.md` | Paper-shaped (*"Clinical brief: a personalised fusion-neoantigen route to treatment in EMC"*, `status: live`) but banner-marked *"EARLIER TREATMENT-TRACK DERIVATIVE… Subsumed by the active manuscript `emc-treatment-roadmap.md`; not the active push."* Live-but-subsumed is not decidable from the file |
| `research/manuscripts/modality-census/novel-modalities.md` | Same shape: full paper title, `status: live`, banner *"EARLIER TREATMENT-TRACK DRAFT — subsumed by the active manuscript"*. Note its fact-check log (`novel-modalities-factcheck.md`) is INTERNAL below, but the paper itself is not resolvable |

#### INTERNAL WORKING RECORD — 126

Correctly outside a submission gate: memos, red-team and review rounds, plans, checklists, audits, verdicts/rulings, registers, generated views, READMEs. Full list, grouped by directory, with frontmatter `kind` in brackets:

**`research/manuscripts/` (6)** — `[manuscript] README.md`; `[memo] REORG-PLAN.md`; `[generated] SUBMISSION-PACKET.md` (evidence: `scope: "Submission logistics only… It reports no result, asserts nothing about any disease or agent, and is not a scientific record"`, `audience: [maintainers]`); `[memo] emc-mortality-mechanisms.md`; `[—] emc-systems-map.md` (banner *"GENERATED FILE — DO NOT EDIT"*, view of `emc-systems-map.json`); `[memo] no-wet-lab-publication-archetypes.md`

**`aso/` (19)** — `[memo] aso-delivery-evidence-2026-08.md`; `[memo] atu027-systemic-sirna-solid-tumour-evidence.md`; `[manuscript] fusion-junction-aso-deposit-stopping-rule.md`; `[manuscript] fusion-junction-aso-guard-coverage-audit.md`; `[manuscript] fusion-junction-aso-paper-redteam-round{2,3,4,5,6,7,8,9,10,12}.md` (10 files); `[memo] fusion-junction-aso-preprint-checklist.md`; `[memo] fusion-junction-aso-submission-plan.md`; `[memo] hybrid-intron-aso-target.md`; `[memo] nat-revision-checklist-2026-08-25.md`; `[memo] review-backlog-2026-08-19.md`

**`aso/submitted-2026-08-21/` (1)** — `[memo] README.md` (*"The 2026-08-21 Research Square submission of PUB-ASO — a historical record"*)

**`care-delivery/` (4)** — `[memo] emc-adaptive-scheduling-pazopanib.md`; `[memo] emc-care-delivery-endpoint-decision.md`; `[memo] emc-oligometastatic-rt-concept.md` (`scope: "Proposal only — this is not the manuscript"`); `[memo] emc-radioresistance-reappraisal.md`

**`degrader/` (32)** — `[memo] degrader-citation-audit-2026-08-08.md`; `[manuscript] four-open-decisions-2026-08-07.md`; `[manuscript] four-open-decisions-RULING-2026-08-07.md`; `[manuscript] nr4a3-congeneric-rbfe-plan.md`; `[manuscript] nr4a3-degrader-broader-indications.md`; `[manuscript] nr4a3-degrader-carT-and-family-druggability-framing.md`; `[manuscript] nr4a3-degrader-figures.md`; `[manuscript] nr4a3-degrader-insilico-completeness.md`; `[manuscript] nr4a3-degrader-paper-positioning.md`; `[manuscript] nr4a3-degrader-paper-redteam.md`; `[manuscript] nr4a3-degrader-paper-review-response.md`; `[manuscript] nr4a3-degrader-preprint-plan.md`; `[historical] nr4a3-degrader-preprint.md` and `[historical] nr4a3-degrader-preprint-si.md` (both `status: superseded`, self-described *"A redirect… it exists ONLY to be found at the path"*, `superseded_by` the covered `nr4a3-degrader-paper{,-SI}.md` — despite their names these are **not** an outward preprint/SI); `[manuscript] nr4a3-degrader-reviewer-revisions-2026-07-15.md`; `[manuscript] nr4a3-degrader-selectivity-architecture.md`; `[manuscript] nr4a3-degrader-strategy-ternary-first.md`; `[manuscript] nr4a3-emc-biology-evidence.md`; `[manuscript] nr4a3-inverse-linker-design-2026-07-25.md`; `[manuscript] nr4a3-orientation-basin-search-2026-07-25.md`; `[manuscript] nr4a3-reach-rule-correction-2026-07-25.md`; `[manuscript] nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md`; `[manuscript] nr4a3-transfer-anchor-and-handle-risk-2026-07-25.md`; `[manuscript] r3-site-choice-audit-2026-08-03.md`; `[manuscript] r5-cross-method-pose-2026-08-06.md`; `[manuscript] selectivity-requirement-sizing.md`; `[manuscript] three-row-audit-2026-08-03.md`; `[manuscript] valB-mini-r0-verdict-2026-07-25.md`; `[manuscript] valB-reviewer-decision-2026-07-17.md`; `[manuscript] valb-calibrator-rescope-2026-07-25.md`; `[manuscript] valb-closure-triangle-pregate-2026-07-25.md`; `[manuscript] valb-gate-defect-fix-audit-2026-07-25.md`

**`dependency/` (7)** — `[register] emc-atr-collaborator-package-changelog.md`; `[manuscript] emc-atr-collaborator-package-peer-review-2026-08-10.md`; `[manuscript] emc-atr-collaborator-package-review-response-2026-08-10.md`; `[memo] emc-dnapk-nr4a3-lane-assessment.md`; `[memo] emc-kinase-leads-source-verification.md`; `[memo] emc-sgk1-lane-assessment.md`; `[memo] emc-tsc-mtor-route.md`

**`endpoint/` (1)** — `[memo] emc-endpoint-alternatives-2026-08-08.md`
**`figures/` (1)** — `[manuscript] README.md`
**`fusion-direct/` (1)** — `[manuscript] fusion-selective-approaches-overview.md`

**`fusion-output/` (8)** — `[manuscript] emc-fourth-cohort-sra-2026-08-08.md`; `[memo] gse243553-eno3-overlap-2026-08-08.md`; `[memo] gse28866-tumour-vs-normal-reading.md`; `[memo] nr4a3-cistrome-search-2026-08-08.md`; `[manuscript] nr4a3-fusion-transcriptional-output-peer-review-2026-08-10.md`; `[memo] nr4a3-fusion-transcriptional-output-repo-notes.md`; `[manuscript] nr4a3-fusion-transcriptional-output-review-response-2026-08-10.md`; `[memo] nr4a3-fusion-transcriptional-output-submission-checklist.md`

**`fusion-partner/` (2)** — `[register] emc-fusion-partner-correction-register.md`; `[register] partner-event-counts-2026-08-08.md`
**`methods-record/` (1)** — `[manuscript] fact-check-log.md`
**`modality-census/` (4)** — `[manuscript] emerging-modalities-scan-emc.md`; `[manuscript] novel-modalities-factcheck.md`; `[manuscript] wet-lab-contracting-costs.md`; `[manuscript] what-a-civilian-can-buy.md`

**`mtap-prmt5/` (8)** — `[manuscript] emc-mtap-prmt5-decline-review-{biology,editor,integrity,statistics}-2026-08-10.md` (4); `[manuscript] emc-mtap-prmt5-decline-review-response-2026-08-10.md`; `[manuscript] emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md`; `[manuscript] emc-mtap-prmt5-hypothesis-review-response-2026-08-10.md`; `[runbook] emc-mtap-prmt5-prepost.md`

**`neoantigen/` (6)** — `[memo] emc-vaccine-path-preprint-checklist.md`; `[memo] emc-vaccine-path-redteam-round1.md`; `[memo] emc-vaccine-path-stopping-rule.md`; `[memo] fusion-breakpoint-prior-art-sweep-2026-08.md`; `[manuscript] immunotherapy-options-emc.md`; `[memo] shared-vs-individualized-neoantigen-evidence.md`

**`occupancy/` (1)** — `[manuscript] cryptic-pocket-atlas-concept.md`

**`program/` (13)** — `[architecture] emc-autonomy-architecture.md`; `[manuscript] emc-post-degrader-options.md`; `[manuscript] emc-treatment-paper-outline.md`; `[memo] emc-unexplored-treatment-lanes.md`; `[manuscript] map-audit-strategy.md`; `[manuscript] map-merge-inventory.md`; `[memo] new-evidence-routes.md`; `[memo] new-evidence-session-prompts.md`; `[manuscript] paper-framing-options.md`; `[manuscript] path-family-synthesis.md`; `[manuscript] preprint-host-decision.md`; `[manuscript] preprint-host-decision-round2.md`; `[manuscript] target-route-options.md`

**`repurposing/` (4)** — `[memo] pparg-direction-emc.md`; `[manuscript] repurposing-hypotheses-peer-review-2026-08-10.md`; `[manuscript] repurposing-hypotheses-review-response-2026-08-10.md`; `[manuscript] repurposing-hypotheses-review.md`

**`surface-targets/` (6)** — `[manuscript] car-t-strategies-emc.md`; `[manuscript] emc-surface-target-landscape-peer-review-2026-08-10.md`; `[manuscript] emc-surface-target-landscape-review-response-2026-08-10.md`; `[manuscript] emc-surface-target-redteam.md`; `[memo] fap-rlt-2026-regrade.md`; `[memo] ofcs-var2csa-lane.md`

**`tcip/` (1)** — `[manuscript] tcip-interface-floor-sizing.md`

### The two counts

| Class | n | Share of 145 |
|---|---|---|
| **OUTWARD-FACING** | **16** | 11.0% |
| **UNKNOWN** | **3** | 2.1% |
| **INTERNAL WORKING RECORD** | **126** | 86.9% |

### Two findings a human should read before acting on the lists

1. ⚠ **`kind: manuscript` in frontmatter is not evidence of anything.** **45 of the 145** uncovered files carry the literal sentence *"Inferred kind `manuscript` from its location under research/manuscripts/"* plus `_backfilled: true` and `purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.` A census that trusted `kind` would grade 88 of 145 as manuscripts. Every classification above rests on a manifest membership, a build-script reference, a `publications.json` row, or a hand-read title/`purpose`/`scope`/body banner — never on a backfilled `kind`.
2. ⭐ **The gap is not random and it is not the model's fault.** The graph-driven half is airtight (26/26 endpoints covered). Everything outward-facing that leaks does so through one of exactly three seams: (a) the **deposited payload** — the ASO deposit ships 12 `.md` files, of which **6 are covered and 6 are not**, with no property distinguishing the two halves (`fusion-junction-aso-working-record.md` covered, `fusion-junction-aso-paper-redteam.md` not, both under the same `correction_record` promise); (b) **correspondence** — 1 cover letter covered by accident of a pinned number, 5 not, 1 outreach file covered and its twin not; (c) **paper-shaped drafts the graph never modelled** (`meta-analysis.md`, the two `fusion-direct` concept papers). No document in these seams needs a *new* gate to be reached — each is one row away from a registry that already exists. **That is a scoping decision for the gate owner, not a worker's call, and I have neither made it nor authored anything toward it.**

## Validation evidence

All rows **RUN**. Environment: this container, `/usr/local/bin/python3` 3.11, stdlib only, no network, no paid API, no GPU. All execution under `/tmp/claude-0/w77/` (now deleted); the repository was read only.

- `git ls-files 'research/manuscripts/*' | grep '\.md$'` → `187`.
- Set computation (`classify.py`) → `denominator 187 / covered 42 / uncovered 145`, exit 0. Per-gate breakdown printed: `claims 36`, `style 13`, `residue 34`, `consistency 16`.
- Cross-product (`evid.py`) → `PAPERS md: 5`, `sm files: 7`, `manifest md files: 12`, `uncovered with any outward signal: 6` — all six in `research/manuscripts/aso/`, all via `aso_deposit: True`, all with `pub: None`.
- `publications.json` check → `publications.json entries with document.file: 26` / `of those, uncovered: 0 []`.
- Channel sweep (`chan.py`) over 11 tracked outward-channel artifacts → 7 uncovered files named; the seventh (`SUBMISSION-PACKET.md`) resolves to a prose comment in `build_submission_parts.py:37`, not a build input, and its own frontmatter reclassifies it INTERNAL.
- `sed -n '2250,2280p' research/manuscripts/build_submission_pdf.py` → `STAMP_SOURCES` verbatim, listing `aso/fusion-junction-aso-submission-tables.md` (`:2263`) and `…-submission-references.md` (`:2264`). `sed -n '420,445p'` → the availability-statement comment quoted above.
- Frontmatter census (`fm.py`) → `('manuscript','live') 88 / ('memo','live') 45 / (None,None) 3 / ('register','live') 3 / ('generated','generated') 2 / ('historical','superseded') 2 / ('runbook','live') 1 / ('architecture','live') 1`. `grep -l "Inferred kind \`manuscript\` from its location" <145 files> | wc -l` → `45`.
- Final partition (`final.py`) asserted `OUT ∪ UNK ⊆ uncovered` and printed `OUTWARD 16 UNKNOWN 3 INTERNAL 126 TOTAL 145`, exit 0.
- **Write isolation**: `git status --porcelain` empty at start and end; no `git` write subcommand was invoked; `PYTHONDONTWRITEBYTECODE=1` on every module-importing run, so no `__pycache__` was created. Scratch deleted and confirmed absent.
- **PROPOSED (NOT RUN), deliberately**: `scripts/preflight.sh` (dispatch forbids); `research/modalities/atr_hrd_sarcoma_series.py` (never invoked in any form); every linter (this run needed their target expressions, not their verdicts, so none was executed — no injection was performed and none was needed); any repair, patch, gate or test — none authored, none proposed as code.
- No content-policy refusal occurred.

## Limitations

- **The 16/3/126 split is a reading of committed documents, not an observation of anything being sent.** Nothing here records that any file has left the building, and classifying a document as outward-facing is a description of its role, never an authorisation to send it. Six of the 16 are demonstrably deposited (the manifest names the DOI); the other ten are ready-to-send or paper-shaped and, as far as this run can tell, **unsent**.
- **The outward/internal line is a judgement on some rows, and I have marked where.** Rows resting on manifest or build-script membership (Group 1) are mechanical. Rows resting on a frontmatter `purpose` or a body banner (Groups 2 and 3) rest on a document's self-description, which is exactly the unfalsifiable-field class W43 characterised. A different reader could reasonably move `nr4a3-degrader-ncs-presubmission-inquiry.md` (a draft) into INTERNAL, or the three Group-3 concept papers into UNKNOWN. The three UNKNOWN rows are the ones I judged genuinely undecidable from committed bytes; they are not a tail of a longer list I stopped grading.
- **Deposit evidence is single-source.** The only per-file deposited manifest in the tree is the ASO one. If another paper is deposited without a tracked manifest, its payload files would score as INTERNAL here — that is UNKNOWN, not absence.
- **Denominator inherited.** `git ls-files 'research/manuscripts/*' | grep '\.md$'` = 187, W51's and W59's exactly. Outward-facing prose elsewhere (`research/modalities/*.md`, `systems/views/`, `archive/manuscripts/`) is outside it and was not classified.
- Nothing here bears on any manuscript's scientific correctness, and nothing computational here bears on EMC efficacy, safety, selectivity or clinical readiness. There is no wet lab and no such claim is made or restated. No manuscript's content is reported as a finding.

## Stop condition

**Set up front:** stop once (a) the uncovered set is recomputed from the same four gate definitions and reconciled against W59's count, (b) every uncovered file is crossed against all five named artifacts with the resulting signal recorded per file, and (c) each file is placed in OUTWARD / INTERNAL / UNKNOWN with a named piece of evidence, with both counts stated — or at ~40 tool calls / ~40 minutes.

**MET**, early, on all three conditions. Returning rather than padding.

## Tool-call and wall-clock count actually used

**27 tool calls** (target ~40). **Wall clock ~4 minutes 21 seconds**, `04:56:38Z` → `05:00:59Z` (target ~40 min).

## Next concrete action

One successor, read-only and bounded, for whoever owns gate semantics — **and the decision itself is a human's, not a worker's**. The 16 outward-facing files split into three seams with three different owners, and only one of them is a measurement question the next worker can settle: **the ASO deposit's 12 `.md` files divide 6 covered / 6 uncovered with no property separating the halves** — same directory, same manifest, same `promises[]` entries in two cases. A successor can settle read-only *why* those 6 are in `lint_claims`/`lint_style`/`lint_submission_residue` and the other 6 are not, by tracing each of the 12 back to the registry row that admitted it (`publications.json` endpoint, `build_submission_pdf.PAPERS`, `lint_style.TARGETS`, `submission-metrics` companion, or `pinned-figures` `must_appear_in`) and reporting whether the admitting property is *deliberate* or *incidental* — W64 already measured that `lint_style.TARGETS` is shrink-guarded but not growth-guarded, so an incidental admission is the expected mechanism. That produces the one thing a gate owner needs and this run could not supply: whether the deposit's coverage split is a policy or an accident. It does not require widening any file set, and I have proposed no repair and authored none. The other two seams (five sibling cover letters; three unmodelled paper-shaped drafts) are scoping decisions with no further measurement available — they should go to the paper owner as the named list above, not to another worker.
