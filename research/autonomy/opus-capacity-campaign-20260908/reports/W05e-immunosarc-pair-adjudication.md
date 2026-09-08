> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Report follows. Working tree untouched (`git status --porcelain` → 0 lines).

---

## Worker

**W05e**, lane 5 refill, OPUS-CAPACITY-CAMPAIGN-20260908. Coordinator: please write this to `research/autonomy/opus-capacity-campaign-20260908/reports/W05e-immunosarc-pair-adjudication.md`.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am `claude-opus-5`. No environment variable names a model; the coordinator must extract the actual per-child served model from the transcript.

`date -u` at start: `Tue Sep  8 02:39:23 UTC 2026`. `date -u` at end: `Tue Sep  8 02:41:57 UTC 2026`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start of run, verbatim, unsorted as emitted):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...,*.svc.cluster.local
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
GLOBAL_AGENT_NO_PROXY=...
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=...
NO_PROXY=...
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=...
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

(Long proxy-list values elided with `...` for readability only; no name/value pair removed except the two `<redacted>` credentials.)

⚠ **HEAD DISCREPANCY, recorded not resolved.** `COMMON-BRIEF.md` §1 names the frozen read commit `92abbcb905cacf07f14b238db50d1b98f6590374`. The actual HEAD I read is **`d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`**, working tree clean. W05d recorded the same drift (`b9a0257→47aac85` during its run). The campaign freeze does not hold; every quotation below is from `d3e9c4d`.

---

## Question

**Does `immunosarc2emc2025` (IMMUNOSARC II, EMC cohort, n=24) share patients with `martinbroto2020immunosarc1` (IMMUNOSARC I, n=68), adjudicated under W05's four-tier rubric applied unrelaxed?**

It is open because `research/modalities/emc-ipd-survival.json` has carried the flag `"⚠ conference abstract; may be an expansion of martinbroto2020immunosarc1"` since it was written, and no rubric verdict has ever been attached to it. W05d measured that this is the corpus's **only** both-documented, same-axis, disjoint-window, shared-institution pair, and named it the decisive successor.

I am asking whether the *publications state an enrolment relationship*. I am **not** attempting patient, case or specimen identity — that is CLOSED-unresolved (Brenca) and I did not go near it.

---

## Prior-work check

Commands run and what they showed:

| # | command | result |
|---|---|---|
| 1 | `grep -rn -i "immunosarc\|NCT03277924" --include='*.json' --include='*.md' --include='*.py' . \| grep -v opus-capacity-campaign \| grep -v '\.git/'` | 35 hits across 20 files; enumerated fully in Method below |
| 2 | `grep -n -i "immunosarc" W05*.md W10c*.md` (campaign reports) | 14 hits, **all in `W05d-tier-b-conjunctivity.md`**; W05, W05b, W05c and W10c never touch this pair |
| 3 | `grep -rl -i "immunosarc" /tmp/claude-0/frozen-corpus/extracted/corpus/` | 20 files, the same set as the live tree |
| 4 | `grep -rn -i "immunosarc" <frozen corpus> \| grep -i -E "tier\|verdict\|OVERLAPPING\|independen"` | 6 hits, **none of them a rubric verdict**. The closest are `emc-systemic-therapy-pooling.json:719` and `systems/graph/routes.json:5173`, which both discuss the *pazopanib*-vs-IMMUNOSARC-II overlap, a different pair |
| 5 | `grep -rn -i "4 (7%)\|four EMC\|4 EMC\|EMC subset not separately\|emc_subset" research/ systems/` | no hit records the stage-1 EMC subgroup count (see Result R6) |

**No rubric verdict on this pair exists in the live tree or the frozen corpus.** This is not a rediscovery.

**Closed items I confirmed I am not replaying**, from `CLOSED-WORK.md`: Brenca case identities (not reopened — I ask about publications, not patients); Hofvander/EGA; paired Davis; promoter transfer; the user-rejected registry ICD-O paper; PUB-EMC-CLASSIFICATION; the NR4A Perspective refusal (not approached under any label). **Denied routes I did not replay:** `ascopubs.org` `/doi/`, `/doi/full/`, `/doi/abs/` and `https://doi.org/` redirect (all 403 per the registry's own `retrievalNote`); Europe PMC for the ASCO DOI (hitCount 0); pazopanib, sunitinib-2014, Wagner 2020, CTARC 2022, trabectedin/RT 2018. I used **PubMed MCP only**, which is a genuinely new route for this pair.

---

## Method / inputs

**Live checkout** `/home/user/Rare-cancers` @ `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`, and the frozen read-only corpus at `/tmp/claude-0/frozen-corpus/extracted/` (consulted for the novelty check only; not overlaid, not copied). Files read: `research/data/emc-clinical-registry.json`, `research/modalities/emc-ipd-survival.json`, `research/modalities/emc_ipd_survival.py`, `research/modalities/emc-scheduling-medians.json`, `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`, `systems/POLICY-evidence.md`, `reports/W05-patient-independence-audit.md`, `reports/W05d-tier-b-conjunctivity.md`.

**Retrieval — PubMed MCP only, with the ⚠ route discipline observed.** Every PMCID was confirmed with `convert_article_ids` **before** `get_full_text_article`, and every returned PMID was checked against what I requested. **Zero mismatches; nothing discarded.**

According to PubMed, the articles retrieved were:

- Martín-Broto J, Hindi N, Grignani G, *et al.* *Nivolumab and sunitinib combination in advanced soft tissue sarcomas: a multicenter, single-arm, phase Ib/II trial.* J Immunother Cancer 2020. PMID 33203665, PMC7674086, [DOI](https://doi.org/10.1136/jitc-2020-001561). CC-BY-NC-4.0.
- Martín-Broto J, Strauss SJ, Palmerini E, *et al.* *IMMUNOSARC II Master Trial: Phase II Study of Sunitinib and Nivolumab in Clear Cell Sarcoma Cohort.* Cancer Commun (Lond) 2026;46:0015. PMID 41836677, PMC12981246, [DOI](https://doi.org/10.34133/cancomm.0015).
- Also surfaced by search, metadata only: Palmerini E, *et al.* *Nivolumab and sunitinib in patients with advanced bone sarcomas.* Cancer 2025;131(1):e35628. PMID 39540661, [DOI](https://doi.org/10.1002/cncr.35628). Moura DS, *et al.* Clin Cancer Res 2024;30:5192-5206. PMID 39283727, [DOI](https://doi.org/10.1158/1078-0432.CCR-24-1782).
- Target of the pair, not retrievable here: Hindi N, Palmerini E, Carrasco-Garcia I, *et al.* J Clin Oncol 2025;43(16_suppl):11513, [DOI](https://doi.org/10.1200/JCO.2025.43.16_suppl.11513).

No expression value, FASTQ, patient record or specimen identifier was accessed or created. No file in the repository was written or edited.

---

## Result

### R1 · Every committed field bearing on the pair, quoted verbatim

**`research/data/emc-clinical-registry.json` → `.registry.citations.immunosarc2emc2025`** — `PRIMARY (committed)`

```
"short": "Hindi 2025 (ASCO abstract)",
"type": "conference-abstract",
"title": "Phase II of sunitinib plus nivolumab in extraskeletal myxoid chondrosarcoma: Results from the GEIS, ISG, and UCL IMMUNOSARC II Study.",
"authors": "Hindi N, Palmerini E, Carrasco-Garcia I, Gonzalez-Billalabeitia E, Valverde C, Strauss SJ, Ibrahim T, Sebio A, Diaz-Beveridge R, Martinez-Trufero J, Stacchiotti S, Collini P, Tirabosco R, Ramos R, Gutierrez A, Moura D, Martin-Broto J.",
"journal": "Journal of Clinical Oncology", "year": 2025, "volume": "43", "issue": "16_suppl", "page": "11513",
"doi": "10.1200/JCO.2025.43.16_suppl.11513",
"license": "publisher (abstract text via Crossref and Semantic Scholar APIs)", "openAccess": false,
"design": "phase 2 histology-specific cohort within the IMMUNOSARC II master trial",
"registration": "NCT03277924", "n": 24,
"population": "adults with advanced, progressing, measurable, centrally confirmed EMC; 9 centres in Spain, Italy and the UK",
"studyPeriod": [2020, 2024], "accessed": "2026-08-07",
"retrievalNote": "ascopubs.org returned HTTP 403 on /doi/, /doi/full/ and /doi/abs/, and https://doi.org/ returned 403 by redirect; Europe PMC returns hitCount 0 for this DOI and PubMed indexes no IMMUNOSARC EMC record. The abstract text was retrieved independently from api.crossref.org (JATS) and api.semanticscholar.org (Graph API) and the two agree token-for-token apart from one HTML entity. ClinicalTrials.gov has no posted results for NCT03277924 (hasResults: false).",
"verified": true
```

**`research/data/emc-clinical-registry.json` → `.registry.citations.martinbroto2020immunosarc1`** — `PRIMARY (committed)`

```
"short": "Martin-Broto 2020 (IMMUNOSARC I)",
"type": "journal-article",
"title": "Nivolumab and sunitinib combination in advanced soft tissue sarcomas: a multicenter, single-arm, phase Ib/II trial.",
"journal": "Journal for ImmunoTherapy of Cancer", "year": 2020,
"pmid": "33203665", "pmcid": "PMC7674086", "doi": "10.1136/jitc-2020-001561",
"license": "CC-BY-NC-4.0", "openAccess": true,
"design": "single-arm phase Ib/II trial, mixed soft-tissue-sarcoma histologies (stage 1 of the same registration as the IMMUNOSARC II EMC cohort)",
"registration": "NCT03277924", "n": 68,
"population": "adults with selected subtypes of advanced soft tissue sarcoma",
"studyPeriod": [2017, 2019], "accessed": "2026-08-07", "verified": true
```

**`research/modalities/emc-ipd-survival.json:235-243`** (identical text at `research/modalities/emc_ipd_survival.py:329-333`) — **the flag under adjudication**

```
"source_id": "immunosarc2emc2025", "n": 24, "endpoint_hint": "pfs",
"why_candidate": "phase 2 histology-specific cohort, sunitinib plus nivolumab",
"full_text_reachable": null, "figure_checked": false,
"overlap_risk": "⚠ conference abstract; may be an expansion of martinbroto2020immunosarc1",
"⚠_caveat": "type is conference-abstract -- abstracts rarely print a numbers-at-risk table, so this may fail the quality floor on reporting completeness alone"
```

**`research/modalities/emc-ipd-survival.json:245-263`** (mirrored at `emc_ipd_survival.py:334-357`) — **the reciprocal flag**

```
"source_id": "martinbroto2020immunosarc1", "n": 68, "endpoint_hint": "pfs",
"why_candidate": "single-arm phase Ib/II; EMC may appear only as a subgroup",
"full_text_reachable": "PMC7674086", "figure_checked": true,
"overlap_risk": "⚠ likely the parent trial of immunosarc2emc2025",
"⚠_caveat": "cohort is advanced soft-tissue sarcoma broadly; an EMC-specific curve may not exist"
```

**`research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`, cohort `immunosarc1_sts_cohort`** — the only committed *reasoning* about the pair

```
"key": "immunosarc1_sts_cohort", "sourceId": "martinbroto2020immunosarc1",
"design_tier": "prospective phase Ib/II, MIXED soft-tissue-sarcoma histologies",
"n_cohort_all_sts": 68, "pfs6_km_pct": 48.0, "pfs6_ci": [41.0, 55.0],
"pool_orr": false,
"pool_reason": "same_registration_as_immunosarc2_and_emc_subset_not_separately_reported",
"quote": "'From May 2017 to April 2019, 68 patients were enrolled: 16 in phase Ib and 52 in phase II... the 6-month progression-free survival rate was 48% (95% CI 41% to 55%).' Trial registration number NCT03277924.",
"why_excluded": "IMMUNOSARC I and the IMMUNOSARC II EMC cohort are stage 1 and stage 2 of the SAME REGISTERED TRIAL, NCT03277924 - visible only in the registry record, whose brief summary reads 'Stage one has two cohorts (soft tissue sarcoma and bone sarcoma) and stage two has eight cohorts (DDCS, EMC, VS, SFT, CCS, ASPS, UPS, LMS and OS)'. The published 48% is the whole mixed-histology stage-1 cohort, not its EMC patients. The accrual windows (2017-2019 vs 2020-2024) do not overlap, so the two do not double-count patients - but a mixed-histology rate cannot enter an EMC pool."
```

**`.../emc-systemic-therapy-pooling.json`, cohort `immunosarc2emc2025`** and **`research/data/emc-clinical-registry.json` → `.treatments.systemicEvidence[0]`**

```
"design": "phase 2 histology-specific cohort inside a master trial (IMMUNOSARC II, stage 2, EMC cohort)",
"evidence_tier": "CONFERENCE ABSTRACT - not peer-reviewed in full, no published tables, no supplementary data, and no results posted at ClinicalTrials.gov (hasResults: false as read 2026-08-07). The sibling cohorts of the same master trial (bone sarcoma, clear cell sarcoma) HAVE full papers; the EMC cohort does not, and Europe PMC indexes no such paper."

"result": "Phase 2 EMC cohort of the IMMUNOSARC II master trial (GEIS/ISG/UCL, NCT03277924), accrued May 2020-July 2024 at 9 centres in Spain, Italy and the UK. Primary endpoint 6-month PFS: 16/23 progression-free (reported as 77%). Best response 2 partial responses, 18 stable, 2 progressive. 12-month OS 90% (95% CI 77-100). CONFERENCE ABSTRACT - no full paper is indexed and ClinicalTrials.gov has no posted results.",
"caveat": "The abstract states its primary endpoint as both 77% and 16/23 (= 69.6%), and its best-response counts sum to 22 rather than the 23 patients it says were evaluable. Both are unreconciled in the only published version of these results."
```

**`.../emc-systemic-therapy-pooling.json` → `residual_overlap_risk`** and **`systems/graph/routes.json:5173`** (mirrored in `systems/views/L2-rt-endpoint-choice.md:59`) — *a different pair, recorded here so it is not confused with mine*

```
"residual_overlap_risk": "NOT ZERO between the two European trials. Both recruited through the Spanish and Italian sarcoma groups, and the IMMUNOSARC II abstract states that 6 of 23 patients had received a prior antiangiogenic - a group that may include patients from the pazopanib trial. ..."
```

Also bearing on the pair: `research/modalities/emc-scheduling-medians.json` `rate_valued` records the misattribution *"48% 6-month PFS"* → *"actually: IMMUNOSARC I's whole mixed soft-tissue-sarcoma cohort"*; `research/literature/emc-ipd-admissibility-2026-08-12.json:181` corrects the KM-figure claim for stage 1; `research/data/emc-clinical-registry.json` → `.outcomes.treatmentResponse[1]` and `.treatments.systemicEvidenceCorrections.superseded[8]` carry the stage-2 result and its supersession note. `research/modalities/emc-hypoxia-therapeutic-status.json:7435` and `emc-hypoxia-confounds.json:5868` carry `"nct": "NCT03277924"` only.

### R2 · The rubric applied unrelaxed

Reproduced verbatim from `W05-patient-independence-audit.md` §1 and applied as written. **I have no authority to change it and did not.**

| tier | condition, as written | met for this pair? | evidence |
|---|---|---|---|
| **A** | "An **explicit non-overlap statement by the authors or depositors** about the specific case sets … or per-case identifiers both reports publish that do not intersect." | **NO** | Neither publication says anything about whether the 24 stage-2 EMC patients include any stage-1 enrollee. Stage 1 predates stage 2's accrual and could not have. The stage-2 publication is a conference abstract with no methods section, no CONSORT, no prior-therapy table beyond "6 of 23 had received a prior antiangiogenic". Neither prints per-case identifiers. |
| **B** | **All three** of disjoint institutions/tissue sources **AND** disjoint accrual windows **AND** disjoint specimen identifier spaces. | **NO — fails on 1 of 3, and that one is unfixable** | **(i) Institutions: FAILS, decisively.** Not merely shared sites — the two are stage 1 and stage 2 of *one registration*, NCT03277924. Stage 1 enrolled at "eight centers in Spain and Italy"; the stage-2 EMC cohort at "9 centres in Spain, Italy and the UK"; the stage-2 CCS sibling at "11 hospitals … in Italy, the United Kingdom, and Spain". Author overlap is near-total (Martín-Broto, Hindi, Palmerini, Valverde, Stacchiotti, Sebio, Ibrahim, Gutiérrez, Martínez-Trufero, Collini, Moura). **(ii) Accrual windows: MET**, and at finer granularity than the registry records — stage 1 "From May 31, 2017 to April 18, 2019"; stage 2 EMC "accrued May 2020-July 2024". Disjoint by ~13 months, not by a year boundary. **(iii) Specimen identifier spaces: NOT DOCUMENTED.** Neither publication prints per-patient or per-specimen identifiers. |
| **C** | "any strict subset of tier B's three conditions" | **YES — this is where the pair lands** | Exactly one of B's three conditions is documented (the accrual windows). Tier C "licenses **nothing on its own**… admissible only as a *falsifier*, never as a *confirmer*." |
| **D** | no evidence at all | n/a | Superseded by C. |

**Overlap side of the asymmetry:** the rubric says `OVERLAPPING` is established "at any tier by a **positive match** — a shared specimen identifier, a shared GSM, a shared bank accession." **No positive match exists.** Shared registration, shared network and shared authors are *shared infrastructure*, not a shared patient. The `overlap_risk` string's wording — "may be an **expansion of**" — is a hypothesis; nothing in either publication asserts it, and the retrieval below makes it less likely rather than more.

### R3 · THE VERDICT

> ## Tier **C** → **UNKNOWN**.
>
> `immunosarc2emc2025` vs `martinbroto2020immunosarc1` is **neither EVIDENCED-INDEPENDENT nor OVERLAPPING**. Tier C licenses nothing. Under the rubric's asymmetry, **UNKNOWN is not a soft yes**: the two `n`s may not be added, the sets may not be called disjoint, and no statement of the form "N distinct EMC patients across both" is licensed.

### R4 · The retrieval, and what it actually decides

The decisive read — does the stage-2 EMC cohort include any stage-1 enrollee? — was attempted through PubMed MCP and **partially answered**. Three findings, each at its own weight:

**(a) `PRIMARY`. IMMUNOSARC I *did* enrol EMC patients — 4 of them.** This is the fact that makes the question live rather than vacuous. From the full text of PMC7674086 (PubMed; [DOI](https://doi.org/10.1136/jitc-2020-001561)), Methods: EMC is a named eligible subtype, chosen for "sensitivity to antiangiogenic compounds (solitary fibrous sarcoma, **extraskeletal myxoid chondrosarcoma**, clear cell sarcoma, alveolar soft part sarcoma …)". Table 1, "Diagnosis (central)": **`Extraskeletal myxoid chondrosarcoma — Phase Ib (n=16): 0 ; Phase II (n=52): 4 (7%)`**. Results: "partial response in patients diagnosed with ASPS (n=2), angiosarcoma (n=1), **extraskeletal myxoid chondrosarcoma (n=1)** and synovial sarcoma (n=1)."

**(b) `PRIMARY`. Neither publication contains an explicit non-overlap statement.** Stage 1's only forward reference is: "Based on the findings of this study, six subtypes of sarcoma were selected for a multicohort phase II trial, which has been recently activated, with the same regimen." That is a design lineage — a *cohort* was selected — and says nothing about patients. Stage 2 exists only as an abstract with no methods. **No tier-A sentence exists to quote.** I will not manufacture one.

**(c) `SECONDARY — protocol-level, and NOT sufficient for tier A.** The closest available evidence is the stage-2 **sibling** cohort's paper (CCS; PMC12981246, PubMed; [DOI](https://doi.org/10.34133/cancomm.0015)), whose Methods list among the IMMUNOSARC II exclusion criteria: **"previous administration of anti-programmed death-1 (PD-1) or anti-PD-ligand 1 (PD-L1), anti-PD-L2, or anti-cytotoxic T-lymphocyte antigen 4 antibody"**, with Table 1 footnote b confirming in that cohort **"None of the patients had received previous TKI or immunotherapy."** Every IMMUNOSARC I enrollee received nivolumab, an anti-PD-1. If that criterion governs the EMC cohort, no stage-1 patient could have entered it.

**Why (c) does not reach tier A, stated plainly.** It is (i) a criterion in a *different cohort's* paper, not a statement about the EMC case sets; (ii) an *inference by transfer* across cohorts of a master trial whose EMC-cohort criteria are unpublished; and (iii) even at full strength it would not rescue tier B, which fails on institutions no matter what. Tier A demands the authors' own sentence about *these* case sets. The rubric does not accept a strong structural argument in its place, and inventing an exception for the one pair where it would be convenient is precisely the relaxation W05d refused. **The verdict stays tier C → UNKNOWN.** What (c) does change is the *direction* of the residual doubt: the `overlap_risk` string's "may be an expansion of" now sits against a documented protocol exclusion pointing the other way.

### R5 · Disposition of the `overlap_risk` flag

**Left explicitly UNKNOWN**, with the missing evidence named exactly. For the coordinator, the flag's status is now: *adjudicated, tier C, UNKNOWN, not converted* — no longer un-adjudicated.

Missing evidence, per unmet condition:

| unmet condition | what specifically is missing | is it obtainable? |
|---|---|---|
| **Tier A** (the only route left) | A sentence in the IMMUNOSARC II EMC cohort's own report stating whether its 24 patients include any of the 4 EMC patients treated in IMMUNOSARC I. Concretely: the EMC cohort's full paper (a CONSORT diagram, a prior-therapy table, or the applied exclusion criteria) — **or** posted per-arm results at ClinicalTrials.gov for NCT03277924. | **Not yet.** PubMed indexes no IMMUNOSARC II EMC paper (measured this run, V4). ClinicalTrials.gov `hasResults: false` as read 2026-08-07. The sibling bone-sarcoma and CCS cohorts have full papers; EMC does not. This is a **wait**, not a blocked route. |
| **Tier B(i)** institutions | Nothing. **Structurally unobtainable** — the two are stages of one registration at overlapping centres, and no future publication can make them institutionally disjoint. | **Never.** ⭐ Therefore **tier B is permanently unreachable for this pair, and tier A is its only possible route to EVIDENCED-INDEPENDENT.** This is the strongest generalisable result here: the pair W05d identified as the sole case where relaxing tier B's conjunction would bite is a pair where relaxation licenses a verdict the *unrelaxed* rubric can never reach on that path. W05d's recommendation stands untouched and unapplied. |
| **Tier B(iii)** identifier spaces | Per-patient or per-specimen identifiers in either report. | Neither publishes any; no IPD exists for either. |

### R6 · ⚠ Two committed statements this retrieval bears on — routed, not applied

Both are `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`, cohort `immunosarc1_sts_cohort`. **I am read-only and did not edit them.**

1. **`why_excluded` asserts: "The accrual windows (2017-2019 vs 2020-2024) do not overlap, so the two do not double-count patients."** That inference — patient-disjointness from window arithmetic alone — is exactly the relaxed-tier-B licence W05d measured as false and declined. Disjoint accrual windows are consistent with a 2018 stage-1 enrollee re-enrolling in 2021; only the anti-PD-1 exclusion (R4c) argues against that, and it is not what the sentence cites. **The pool exclusion itself is unaffected** — it stands on its second, correct ground, "a mixed-histology rate cannot enter an EMC pool". Only the parenthetical inference is over-strong. Smallest correct repair: replace the clause with *"the accrual windows are disjoint (31 May 2017–18 Apr 2019 vs May 2020–Jul 2024), which is one of tier B's three conditions and does not on its own establish patient-disjointness (W05e: tier C → UNKNOWN)."*
2. **`pool_reason: "same_registration_as_immunosarc2_and_emc_subset_not_separately_reported"`** — the second half is imprecise. IMMUNOSARC I's EMC subset **is** partly separately reported: **n = 4 in phase II (Table 1) with 1 RECIST partial response**. What is *not* separately reported is an EMC-specific PFS or 6-month PFSR. No repository file records the count of 4 (prior-work check #5). Routed to the registry owner as a candidate `PRIMARY` addition.

### R7 · Pooling — settled before it is asked

`systems/POLICY-evidence.md` §2.3: *"Across studies: single-institution series are often subsets of national or SEER registries. Where populations may overlap, the **smaller/overlapping** cohort is marked `pool: false` with `contextReason: "population-overlap"`."* §2.7(d): *"§2.1 and §2.3 bind unchanged. Only non-overlapping populations may be combined, and the smaller of any overlapping pair stays `pool: false` with its reason recorded."*

**This adjudication licenses no pooling change in either direction, and I added neither cohort to any denominator.** §2.3 already places the smaller/overlapping member at `pool: false` by default, and `immunosarc1_sts_cohort` is already `pool_orr: false` / `pool_dc: false` on an independent and correct ground (a mixed-histology rate cannot enter an EMC pool). A hypothetical future tier-A statement would still not admit stage 1 into the EMC pool, because its EMC arm is n=4 with no EMC-specific time-to-event data. **The pooling half of this question is moot, exactly as W05d predicted.**

---

## Validation evidence

### RUN

Environment for all shell commands: `/home/user/Rare-cancers`, Linux 6.18.44-fc-v24, `bash`, `python3` (stdlib `json` only), repo HEAD `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`.

| # | command | exit | key verbatim output |
|---|---|---|---|
| 1 | `date -u` (start) | 0 | `Tue Sep  8 02:39:23 UTC 2026` |
| 2 | `git rev-parse HEAD` | 0 | `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4` |
| 3 | `git status --porcelain \| wc -l` (end) | 0 | `0` — **no repository file created, edited or deleted** |
| 4 | `grep -rn -i "immunosarc\|NCT03277924" --include='*.json' --include='*.md' --include='*.py' .` | 0 | 35 hits / 20 files; the `overlap_risk` flag located at `emc-ipd-survival.json:241` and `emc_ipd_survival.py:332` |
| 5 | `python3 -c "<walk emc-clinical-registry.json for immunosarc/NCT03277924>"` | 0 | 5 record paths: `.outcomes.treatmentResponse[1]`, `.registry.citations.immunosarc2emc2025`, `.registry.citations.martinbroto2020immunosarc1`, `.treatments.systemicEvidenceCorrections.superseded[8]`, `.treatments.systemicEvidence[0]` — all quoted at R1 |
| 6 | `grep -n -A12 "2.3" systems/POLICY-evidence.md` | 0 | §2.3 and §2.7(d) quoted at R7 |
| 7 | `grep -rl -i "immunosarc" /tmp/claude-0/frozen-corpus/extracted/corpus/` | 0 | 20 files, same set as live tree |
| 8 | `grep -rn -i "immunosarc" <frozen corpus> \| grep -i -E "tier\|verdict\|OVERLAPPING\|independen"` | 0 | 6 hits, **none a rubric verdict on this pair** |
| 9 | `date -u` (end) | 0 | `Tue Sep  8 02:41:57 UTC 2026` |

**Retrieval calls — PubMed MCP, route discipline observed:**

| # | call | outcome |
|---|---|---|
| V1 | `convert_article_ids(ids=["PMC7674086"], id_type="pmcid")` | `{"pmcid":"PMC7674086","pmid":"33203665","doi":"10.1136/jitc-2020-001561","requested-id":"PMC7674086"}` — ✓ matches the registry's `pmid`/`pmcid`/`doi` exactly. Confirmed **before** any full-text call. |
| V2 | `get_full_text_article(["PMC7674086"])` | 200, full text returned; identifiers echoed `PMC7674086 / 33203665 / 10.1136/jitc-2020-001561` — ✓ **requested = returned**, no mismatch. Yielded R4(a), R4(b). |
| V3 | `convert_article_ids(ids=["41836677"], id_type="pmid")` | `{"pmcid":"PMC12981246","pmid":"41836677","doi":"10.34133/cancomm.0015"}` — ✓ confirmed **before** V5. |
| V4 | `search_articles("(sunitinib AND nivolumab AND \"extraskeletal myxoid chondrosarcoma\") OR (\"IMMUNOSARC II\"[All Fields])")` | `{"pmids":[],"total_count":0}`. ⚠ Reported honestly with its defect: `query_translation` shows PubMed **dropped the `OR ("IMMUNOSARC II")` clause**, so only the first conjunct was executed. That conjunct returning 0 **independently confirms**, by a route never used before for this record, the registry's `retrievalNote` claim that "PubMed indexes no IMMUNOSARC EMC record". **A zero result is UNKNOWN, not proof of absence** — it means no such paper is *indexed in PubMed as of this run*. |
| V5 | `get_full_text_article(["PMC12981246"])` | 200, full text returned; identifiers echoed `PMC12981246 / 41836677 / 10.34133/cancomm.0015` — ✓ **requested = returned**. Yielded R4(c). |
| V6 | `search_articles("IMMUNOSARC AND (extraskeletal myxoid chondrosarcoma OR sarcoma)")` + `get_article_metadata(["41836677","39540661","39283727"])` | 3 PMIDs, all three returned and all three matched what was requested. No IMMUNOSARC II **EMC** record among them. |

**Zero PMID/PMCID mismatches occurred; nothing had to be discarded.** No denied route was replayed: `ascopubs.org`, the `doi.org` redirect and Europe PMC were **not** contacted. No content-policy refusal was encountered at any point.

### PROPOSED (NOT RUN)

- Re-running this adjudication when the IMMUNOSARC II EMC cohort's full paper is indexed, reading its exclusion criteria and CONSORT for a tier-A sentence. **Not run: the paper does not exist in PubMed as of 2026-09-08 (V4).**
- Reading the IMMUNOSARC II protocol from PMC12981246's Supplementary Materials, which may carry the master-trial criteria applying to all eight stage-2 cohorts. **Not run: the MCP full-text tool returns article body text only; supplementary files were not retrievable through the permitted route, and I did not attempt another one.**
- Applying the two R6 repairs. **Not run: I am READ-ONLY on the working tree, and W05 owns the rubric.**

---

## Limitations

- **The verdict is bookkeeping about patient-identity claims. No clinical claim is made or implied**, about sunitinib, nivolumab, EMC or any patient. Nothing here says a treatment works.
- **Tier A was not reached and I did not lower the bar to reach it.** The structural argument at R4(c) is genuinely strong and genuinely insufficient; both halves of that sentence are load-bearing. A reader who takes R4(c) as licensing "these are disjoint patients" has misread this report.
- **Transfer limit:** R4(c) is evidence about the **CCS** cohort. Its transfer to the EMC cohort rests on the assumption that IMMUNOSARC II's exclusion criteria are uniform across its eight stage-2 cohorts. That assumption is plausible and **unverified**.
- **Denominator gap:** this changes no denominator. The number of distinct EMC patients across the two publications remains **UNKNOWN**, bounded above by 24 + 4 = 28 and below by 24.
- **Absence is not proof:** V4's empty result means no such record is indexed in PubMed today. A paper may be in press, under embargo, or indexed elsewhere.
- **Rare-disease base rate** (carried forward from W05 §Limitations): at roughly one case per million per year, cross-study patient reuse is *more* likely than in common cancers, and the two arms here share a referral network. That is why the rubric's conservatism is right for this pair specifically.
- **Frozen-corpus limits per `CORPUS-CONTEXT.md`:** the corpus is a selected snapshot, not a `93b` checkout; `absent_files` is Unknown; local absence is not repository-wide absence. My novelty claim (no prior rubric verdict on this pair) is bounded by both the live `d3e9c4d` tree and that snapshot.
- **The campaign freeze did not hold** (HEAD `d3e9c4d` ≠ the brief's `92abbcb`). Anything I quote is true of `d3e9c4d`.

---

## Stop condition

**Set:** every committed field bearing on the pair quoted verbatim with file and path; the rubric applied unrelaxed with a tier and a verdict; the retrieval attempted through the permitted route with its outcome recorded; the `overlap_risk` flag either converted or left explicitly UNKNOWN with the missing evidence named.

**MET, all four.** Fields at R1 (7 records across 5 files, verbatim). Rubric at R2, verdict at R3 (**tier C → UNKNOWN**), with the specific missing evidence named per unmet condition at R5. Retrieval at R4 and V1–V6: PubMed MCP only, every PMCID confirmed by `convert_article_ids` first, zero mismatches, no denied route replayed, no refusal encountered. Flag left **explicitly UNKNOWN** at R5 — not converted, and not softened into a yes. No repository file written (V3, exit 0, `0` lines). No cohort added to any denominator; §2.3 read first and its consequence stated at R7.

---

## Tool-call and wall-clock count actually used

**16 tool calls** (7 Bash, 1 ToolSearch, 6 PubMed MCP retrieval calls across 4 blocks, 2 further greps folded into Bash) against a ~40 target. **Wall clock 02:39:23 → 02:41:57 UTC = 2 min 34 s** against a ~40 min target. Returned as soon as the stop condition was met; no padding.

---

## Next concrete action

**One task, and it is a *wait* with a trigger, not a research task — which is the honest successor here.**

`immunosarc2emc2025` vs `martinbroto2020immunosarc1` is now adjudicated: **tier C → UNKNOWN**, with tier B shown *permanently unreachable* (shared registration) and tier A shown *blocked only by publication lag*. There is no further read that moves it. The successor is therefore: **when the IMMUNOSARC II EMC cohort's full paper is indexed (its bone-sarcoma and CCS siblings both now have one), read its exclusion criteria and CONSORT for a tier-A sentence and re-run R2.** Until then the verdict stands unchanged, and re-searching PubMed for it is a DUPLICATE of V4.

**Two smaller items are actionable now and are routed, not applied**, both to `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` and both at R6: (1) the `why_excluded` clause inferring patient-disjointness from window arithmetic — a wording defect that does not disturb the pool exclusion; (2) `pool_reason`'s "emc_subset_not_separately_reported", when IMMUNOSARC I's Table 1 gives **4 EMC patients with 1 partial response** and no repository file records it. Item (2) is a candidate `PRIMARY` addition for the registry owner, and it must **not** be pooled.

**W05d's recommendation (keep tier B's conjunction; add a `periodBasis` field rather than relax a tier) is untouched, unapplied, and — on this evidence — strengthened:** the sole pair where relaxation would have bitten turns out to be a pair the unrelaxed rubric can never admit at tier B on any future evidence, so the relaxation's only measured effect would have been to license a false verdict.
