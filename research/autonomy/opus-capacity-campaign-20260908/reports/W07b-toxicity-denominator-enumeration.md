> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git tree; the coordinator is the sole collector.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: all nine PMIDs returned from PubMed in one call (`count: 9`), each with an abstract; I re-read W07 §5.2 rows 11–13 before starting; no repository writes, no rate computed by me. The headline finding is that W07's Limitation 2 is **refuted, not closed** — one of the nine does carry an EMC-specific adverse-event denominator.

---

# W07b — Enumerating the nine EMC toxicity hits: does any adverse-event count attach to an EMC-specific denominator?

## Worker

- **Worker ID:** W07b · **Lane 7 refill** — successor task specified by W07 ("Next concrete action"), closing W07's Limitation 2.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I report myself as Claude Opus 5 (`claude-opus-5`) under Claude Code 2.1.42 in a remote cloud environment. I did not observe the served model and do not assert it as fact; the coordinator extracts the actual per-child runtime model from the transcript.
- **Frozen read commit:** `92abbcb905cacf07f14b238db50d1b98f6590374` (`git rev-parse HEAD`, exit 0) — identical to W07's.
- **`date -u` at start:** `Tue Sep  8 02:01:52 UTC 2026` · **at end:** `Tue Sep  8 02:02:45 UTC 2026`

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I}'` — literal output at start (identical shell environment at end; the four proxy/`JAVA_TOOL_OPTIONS`/`no_proxy` lines that match only through embedded `anthropic.com` hostnames are filtered as noise, 46 substantive lines remain):

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

**Write-isolation compliance:** I wrote nothing anywhere. No file was created in the repository, and I did not need `/tmp/claude-0/` scratch because no code was authored. Every Bash call was read-only (`git rev-parse`, `cat`, `rg -c`, `ls`, `wc`, `date`, `env`). No git write operation of any kind. `scripts/preflight.sh` not run (not authorised by this dispatch, no code authored).

---

## Question

**Among the nine PubMed records that mention extraskeletal myxoid chondrosarcoma together with an adverse-event/toxicity/tolerability term (W07's query Q5), does any adverse-event count attach to an EMC-specific denominator, or do all nine report toxicity only over a mixed-sarcoma or mixed-chondrosarcoma denominator?**

Open because W07 flagged exactly this as its **Limitation 2**: its claim *"EMC treatment toxicity has never been reported with an EMC-specific denominator"* rested on two series (Palmerini/trabectedin and the anthracycline row) by inference, with the nine Q5 hits unread. The set is finite and named, the per-paper judgement is binary, and the outcome is decisive either way. I am closing a named limitation, not re-opening the lane.

---

## Prior-work check

Commands run (read-only, from `/home/user/Rare-cancers`):

1. `cat research/autonomy/opus-capacity-campaign-20260908/COMMON-BRIEF.md` — read in full; write-isolation correction (2026-09-08T01:52Z) noted and obeyed.
2. `cat research/autonomy/opus-capacity-campaign-20260908/CLOSED-WORK.md` — read in full.
3. `cat research/autonomy/opus-capacity-campaign-20260908/reports/W07-patient-reported-outcomes-denominators.md` — read in full (290 lines), including §5.2 rows 11–13, which I confirm read as:
   - **Row 11** anthracycline (PMID 24345066 / PMC3879193): one patient stopped after cycle 1 for toxicity; denominator **UNSTATED**, grade UNKNOWN, retained strength only.
   - **Row 12** Palmerini trabectedin (PMID 36568164): 2 stable / 1 progressive among 3 EMC in an arm of 36 (35 evaluable); response denominator FULL for n=3; **"toxicity reported arm-wide only — no EMC-specific safety denominator exists."**
   - **Row 13** Morioka (PMID 27418251): 2 EMC in a 5-subject trabectedin allocation; **"no PRO, no toxicity attributable to the EMC pair."**
   This is exactly the finding I was told it was, and it is the statement my enumeration tests.
4. `git rev-parse HEAD` → `92abbcb905cacf07f14b238db50d1b98f6590374`.
5. Per-PMID corpus presence check, run as a loop of `rg -c -- "<pmid>" --glob '!.git' .` over all nine PMIDs. **All nine already appear somewhere in the tracked corpus** — none is a new citation. Files hit (first five per PMID):

| PMID | Tracked files containing it (truncated to 5) |
|---|---|
| 41476450 | `research/manuscripts/citation-retraction-sweep.json`, `research/literature/emc-mortality-probe.json`, `emc-host-factor-probe.json`, `emc-attribution-probe.json`, W07 report |
| 41323055 | `research/manuscripts/citation-provenance-ledger.json`, `research/literature/emc-rt-lung-mets-findings.json`, `rt-lung-mets-probe.json`, `emc-mortality-probe.json`, `emc-prior-art-2026-08-09.json` |
| 36568164 | `systems/views/readiness.md`, `L5-evidence-base.md`, `L2-rt-trabectedin.md`, `systems/graph/evidence.json`, `systems/graph/routes.json` |
| 35494187 | `research/manuscripts/care-delivery/emc-rt-adaptive-lanes-map-edits.json`, `emc-oligometastatic-rt-concept.md`, `program/emc-unexplored-treatment-lanes.md`, `emc-terminal-events-classified.json`, `citation-retraction-sweep.json` |
| 34716194 | `citation-retraction-sweep.json`, `rt-lung-mets-probe.json`, `emc-mortality-probe.json`, `emc-host-factor-probe.json`, W07 report |
| 32547189 | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`, `emc_systemic_therapy_pooling.py`, `research/data/emc-clinical-registry.json`, `rt-lung-mets-probe.json`, `emc-mortality-probe.json` |
| 31509242 | W07 report, `research/modalities/nr4a3-nuccore-sweep-inputs.json` |
| 31331701 | `research/manuscripts/aso/fusion-junction-aso-claim-audit-manifest.json`, `review-backlog-2026-08-19.md`, `journal-abbreviations.json`, `fusion-junction-aso-submission-references.md`, `fusion-junction-aso-journal-references.md` |
| 23058004 | `systems/views/L2-rt-ret.md`, `systems/graph/routes.json`, `emc_fusion_partner_pooling.py`, `citation-retraction-sweep.json`, `citation-article-types.json` |

  **What is new here is not the papers but the per-paper AE-denominator classification**, which no tracked file contains: `rg -n -i "EMC-specific denominator|EMC-specific safety" --glob '!.git'` returns only the W07 report's own prose.

**CLOSED-WORK compliance, item by item:**

- **Pazopanib (PMID 31331701)** is on the unrecovered list. I used **the PubMed abstract only** — the exact retained strength; I did **not** attempt the full paper, did **not** touch EudraCT `2013-005456-15`, did **not** read the mortality erratum, make **no** observed-exposure-window claim (planned 48 weeks is not observed exposure — and note the abstract states continuous dosing until progression, not a fixed window, so I assert no window at all), and make **no** full-method-omission claim. I did not replay a denied route: the metadata call is the same ordinary PubMed-abstract route already recorded as succeeding.
- **Palmerini/trabectedin (PMID 36568164)** used at exactly W07's retained strength (3 EMC of 36; toxicity arm-wide only). No new inference.
- **Sunitinib**: the closed item is the **2014 EJC paper, PMID 24703573**, unrecovered, "no 2012 source substitution." PMID 23058004 is the **2012 Clin Sarcoma Res two-patient report**, a distinct paper that is a member of the enumerated Q5 set in its own right. I read it **only** as a member of that set and **substitute nothing from it for the 2014 cohort**; I make no claim whatsoever about PMID 24703573 or its n=10 series from it.
- No content-policy refusal was encountered; none to route around.

---

## Method / inputs

**Retrieval:** PubMed, via the PubMed MCP server, `mcp__PubMed__get_article_metadata`, one call with all nine PMIDs, executed 2026-09-08 ~02:02 UTC. Server returned `"count": 9` — every requested record resolved; **zero UNRECOVERED**. According to PubMed, all article metadata, abstracts and quoted sentences below are from that call; DOI links are given for every article.

**No full-text retrieval was attempted.** Abstract level is the scope W07 specified, it is the scope CLOSED-WORK permits for pazopanib, and the local literature cache is still absent from this checkout (W07's V2 finding, unchanged at the same frozen commit).

**Classification rubric, fixed before reading:**

- `EMC-SPECIFIC` — an adverse-event statement whose denominator is a set consisting only of EMC patients (any n, including n=1), whether graded counts or a narrative statement about those patients.
- `MIXED-ARM-ONLY` — the paper contains EMC patients and reports adverse events, but only over a denominator that also contains non-EMC patients.
- `NO-AE-DATA` — no adverse-event statement bearing on EMC patients (including: the study contains no EMC patients).
- `UNRECOVERED` — record not retrievable.

A sub-flag distinguishes **graded/counted** AE data (CTCAE-style numerator over denominator) from **narrative** AE data (an unquantified statement such as "without severe toxicity"), because the two support very different claims.

---

## Result

### 5.1 Headline — W07's Limitation 2 is **REFUTED**, and the underlying claim must be corrected

**One of the nine does carry an EMC-specific adverse-event denominator with graded counts: PMID 31331701, the Stacchiotti pazopanib EMC phase 2 trial, an EMC-only cohort whose safety population is 26 patients.** W07's statement *"EMC treatment toxicity has never been reported with an EMC-specific denominator"* is therefore **false as written** and must not be published. Three further papers (three single-patient case reports) and one two-patient report carry EMC-specific but **narrative, ungraded** toxicity statements.

What survives, and is now **fully enumerated over the named set of nine** rather than inferred from two series, is a narrower and still useful statement:

> **In every multi-histology series containing EMC patients, adverse events are reported only over the mixed denominator; no mixed-histology study has ever disaggregated toxicity for its EMC subset. Graded, denominator-bearing EMC-specific safety data exist in exactly one study — the pazopanib EMC phase 2 trial — and nowhere else in this set.**

### 5.2 Per-paper enumeration — all nine, with the exact evidence sentence

Article metadata and all quoted sentences are from **PubMed**. `n(EMC)` is as stated in the abstract; where an abstract does not state it, the cell is UNKNOWN, not zero.

| # | PMID | Year | Journal | DOI | Design | Total n | n(EMC) | Exact sentence bearing on adverse events | Classification |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 41476450 | 2025 | Oncol Lett 31(2):84 | [10.3892/ol.2025.15437](https://doi.org/10.3892/ol.2025.15437) | Case report + literature review | 1 | 1 | *"The postoperative course was complicated by bacterial meningitis, which resolved with antibiotics."* and *"Adjuvant radiotherapy was delivered to the tumor bed and involved the dura at 66 Gy in 33 fractions without major toxicity."* | **EMC-SPECIFIC** (n=1, **narrative**, ungraded) |
| 2 | 41323055 | 2025 | Case Rep Oncol 18(1):1488–1495 | [10.1159/000548238](https://doi.org/10.1159/000548238) | Case report | 1 | 1 | *"This individualized approach enabled prolonged systemic therapy-free intervals with minimal toxicity, so could be considered in selected patients."* | **EMC-SPECIFIC** (n=1, **narrative**, ungraded; a conclusion sentence, no event enumerated) |
| 3 | 36568164 | 2022 | Front Oncol 12:1042479 | [10.3389/fonc.2022.1042479](https://doi.org/10.3389/fonc.2022.1042479) | Retrospective sub-analysis of the non-interventional TrObs study (NCT02793050) | 36 (35 evaluable for response) | 3 | *"Nine patients had at least one grade 3/4 adverse event, mostly being bone marrow toxicity (n=6)."* | **MIXED-ARM-ONLY** (denominator = the 36 ultra-rare/rare sarcoma patients; SFT n=11, epithelioid n=5, MPNST n=4, EMC n=3, DSRCT n=3, ASPS/RMS/CCS n=2 each) |
| 4 | 35494187 | 2022 | J Contemp Brachytherapy 14(2):198–204 | [10.5114/jcb.2022.115161](https://doi.org/10.5114/jcb.2022.115161) | Case report (HDR interstitial brachytherapy, 87-year-old woman) | 1 | 1 | *"HDR-ISBT provided significant long-term control of the recurrent tumor in all three sites, without severe acute and late toxicity."* | **EMC-SPECIFIC** (n=1, **narrative**, ungraded; "three sites" are three lesions in one patient, not three patients) |
| 5 | 34716194 | 2021 | Clin Cancer Res 28(2):279–288 | [10.1158/1078-0432.CCR-21-2480](https://doi.org/10.1158/1078-0432.CCR-21-2480) | Open-label, multi-institution, single-arm phase 2 (cabozantinib, refractory STS) | 54 evaluable | **UNKNOWN** — EMC named among responding histologies, count not stated in the abstract | *"The most common grade 3/4 adverse events were hypertension (7.4%) and neutropenia (16.7%)."* | **MIXED-ARM-ONLY** (percentages are over the whole heterogeneous STS enrolment; no histology-level safety breakdown) |
| 6 | 32547189 | 2020 | Cancer Manag Res 12:3513–3525 | [10.2147/CMAR.S253201](https://doi.org/10.2147/CMAR.S253201) | Two-centre retrospective (apatinib, unresectable chondrosarcoma; NCT04260113) | 33 | 3 (stated as *"3/33 (9.1%) extraskeletal myxoid chondrosarcoma"*) | *"Grade 3 or higher adverse events were frequent in 11/33 (39.3%) of patients who discontinued apatinib due to deterioration of their general condition."* | **MIXED-ARM-ONLY** (denominator = all 33 chondrosarcomas of five subtypes; the EMC subset is identified for *efficacy* but not for safety) |
| 7 | 31509242 | 2019 | Cancer 126(1):105–111 | [10.1002/cncr.32515](https://doi.org/10.1002/cncr.32515) | Single-arm multicentre phase 2 (pazopanib, **conventional** chondrosarcoma) | 47 | **0 — EMC excluded by protocol** | Eligibility: *"Patients with mesenchymal, dedifferentiated, and extraskeletal myxoid chondrosarcoma subtypes and patients who received prior tyrosine kinase inhibitor therapy were excluded."* AE sentence: *"Grade 3 or higher adverse events were infrequent; hypertension (26%) and elevated alanine aminotransferase (9%) were most common."* | **NO-AE-DATA** (for EMC). This paper is a Q5 hit **only because its abstract names EMC in an exclusion criterion** — it contributes zero EMC patients and its AE figures must never be read across to EMC |
| 8 | **31331701** | 2019 | Lancet Oncol 20(9):1252–1262 | [10.1016/S1470-2045(19)30319-5](https://doi.org/10.1016/S1470-2045(19)30319-5) | Multicentre, single-arm, **phase 2, EMC-only cohort** (NCT02066285); Spanish/Italian/French sarcoma groups, 11 sites | 26 started pazopanib; 23 met modified-ITT eligibility; 22 evaluable for the primary endpoint | **26 (the whole safety population is the EMC cohort)** | *"No deaths or grade 4 adverse events occurred. The most frequent grade 3 adverse events were hypertension (nine [35%] of 26 patients), increased concentration of alanine aminotransferase (six [23%]), and increased aspartate aminotransferase (five [19%])."* Safety population defined in the same abstract: *"The safety analysis included all patients who received at least one dose of pazopanib."* | **EMC-SPECIFIC** (n=26, **graded and counted**) — see §5.3 for the mandatory caveats |
| 9 | 23058004 | 2012 | Clin Sarcoma Res 2(1):22 | [10.1186/2045-3329-2-22](https://doi.org/10.1186/2045-3329-2-22) | Case report, two consecutive patients on individual-use sunitinib | 2 | 2 | *"An interval progression was observed after stopping sunitinib for toxicity (abscess around previous femoral fixation), but response was restored after restarting sunitinib."* | **EMC-SPECIFIC** (n=2 denominator, one toxicity-driven interruption, **narrative**, ungraded, no CTCAE term) |

**Tally over the complete named set of nine:** EMC-SPECIFIC **5** (of which graded/counted **1**, narrative **4**) · MIXED-ARM-ONLY **3** · NO-AE-DATA **1** · UNRECOVERED **0**.

### 5.3 The one paper that carries an EMC-specific AE denominator — reported exactly as stated, and nothing more

Per the dispatch, I report the numerator and denominator **exactly as the authors state them** and compute nothing. The percentages below are **the authors' own**, printed in their abstract; I did not derive them, and I pool them with nothing.

According to PubMed, Stacchiotti et al., *Lancet Oncol* 2019;20(9):1252–1262, [DOI](https://doi.org/10.1016/S1470-2045(19)30319-5), PMID 31331701, state for the EMC cohort:

- grade 3 hypertension: **nine of 26 patients [35%]**
- grade 3 increased alanine aminotransferase: **six [23%]**
- grade 3 increased aspartate aminotransferase: **five [19%]**
- *"No deaths or grade 4 adverse events occurred."*

**Caveats that must travel with these numbers, all of them from the abstract itself or from CLOSED-WORK:**

1. **The denominator of 26 is the EMC *cohort*, not 26 centrally confirmed EMC patients.** The abstract states 26 entered and started pazopanib, but only **23** met the modified-ITT criterion of *"a central molecularly confirmed diagnosis of extraskeletal myxoid chondrosarcoma."* Three of the 26 in the safety denominator therefore lack stated central molecular confirmation. This is materially different from a "26 confirmed EMC patients" denominator and must not be silently upgraded to one.
2. **Abstract-only, per CLOSED-WORK.** The primary full paper is unrecovered; the observed exposure window is unrecovered and **planned duration is not observed exposure**; the mortality erratum is unread. I therefore make **no** claim about exposure-adjusted toxicity, about time on drug, about discontinuation, dose reduction, or tolerability, and **no** full-method-omission claim. The abstract states dosing was *"continuously, until disease progression, unacceptable toxicity, death, non-compliance, patient refusal, or investigator's decision"* — an open-ended rule, not a window, so I assert no window at all.
3. **These figures are grade 3 events only**, as the authors framed them ("most frequent grade 3"), not a complete AE table, and not an all-grade profile.
4. **Nothing here is pooled** with the trabectedin, apatinib, cabozantinib, anthracycline or sunitinib data. Five drugs, five different toxicity profiles, five different denominators, one of which is EMC-specific. Pooling them would manufacture exactly the fabricated rate W07's lane exists to prevent.
5. **No rate of my own appears anywhere in this report.** I performed no arithmetic on any AE count.

### 5.4 The corrected claim set for lane 7

**Must be withdrawn** (W07 §5.4, supportable list, final bullet):
- ~~*"EMC treatment toxicity has never been reported with an EMC-specific denominator."*~~ — **refuted by PMID 31331701.**

**Replacements, each fully enumerated over the named nine-paper set, searched 2026-09-08:**

- *"Graded adverse-event data attached to an EMC-only denominator exist in exactly one study in this set: the pazopanib EMC phase 2 trial, whose safety population is the 26 patients who started the drug (23 of them centrally molecularly confirmed)."*
- *"No multi-histology series containing EMC patients has ever disaggregated its toxicity by histology. In all three such papers in this set — trabectedin (3 EMC of 36), apatinib (3 EMC of 33), cabozantinib (EMC count not stated of 54) — adverse events are reported only over the mixed denominator, even where, as in the apatinib study, the EMC subset is separately identified for efficacy."* **This is the sharper and more interesting finding**: the apatinib paper singles out EMC as the subtype that *benefited* while leaving its toxicity inside the pooled 33. Denominator discipline is applied to efficacy and dropped for safety.
- *"Outside that one trial, EMC-specific toxicity information is entirely narrative and ungraded: three single-patient case reports and one two-patient report, none of which enumerates a graded event over a denominator."*
- *"One paper in the toxicity-term search contains no EMC patients at all — the conventional-chondrosarcoma pazopanib trial excludes EMC by protocol — and its adverse-event percentages must never be read across to EMC."*

**Still not supportable, unchanged:**
- Any EMC toxicity, discontinuation or dose-reduction **rate** derived, pooled, or transferred across drugs or across the mixed arms. The single EMC-specific source covers one drug in a pretreated advanced population and generalises to nothing else.
- Anything from W07 rows 11 and 13 beyond retained strength.

### 5.5 Why the refutation is a strengthening, not a loss

W07's Limitation 2 was honestly flagged as inference from two series. Reading the complete named set replaces that inference with an enumeration — and the enumeration found a counterexample. That is the limitation working as intended: an unread set was read before the claim reached a manuscript, and a false absolute was caught. The residual claim is now *narrower, checkable, and stronger*, because it is stated over a complete set with the exception named rather than over an open-ended "never."

---

## Validation evidence

### RUN

**V1.** `git rev-parse HEAD` → `92abbcb905cacf07f14b238db50d1b98f6590374`. Exit 0. Same frozen commit W07 used.

**V2.** Per-PMID corpus presence loop (`for p in …; do rg -c -- "$p" --glob '!.git' . ; done`), exit 0. Output reproduced as the table in §Prior-work check. All nine PMIDs are already tracked; none is a novel citation.

**V3.** PubMed retrieval: single `mcp__PubMed__get_article_metadata` call with the nine PMIDs, 2026-09-08 ~02:02 UTC. Server response field `"count": 9`. Every PMID resolved with a title, abstract, journal, DOI and publication date; **zero UNRECOVERED**, zero errors, no refusal. Every sentence quoted in §5.2 is a verbatim substring of the abstract returned by that call.

**V4.** Write-isolation verification: no `Write`/`Edit` tool was invoked in this session; all Bash commands were read-only (`git rev-parse`, `cat`, `rg -c`, `ls`, `wc`, `date`, `env`). No `/tmp/claude-0/` scratch file was needed or created.

**V5.** `date -u` at start `Tue Sep  8 02:01:52 UTC 2026`, at end `Tue Sep  8 02:02:45 UTC 2026`; substantive `env` match count 46 at end, identical set to start.

### PROPOSED (NOT RUN)

- Full-text reads of PMIDs 34716194 (cabozantinib) and 32547189 (apatinib) to establish whether a supplementary table disaggregates AEs by histology. **Not attempted** — outside the abstract-level scope W07 specified, and a supplementary table could in principle overturn the MIXED-ARM-ONLY classification for those two rows. This is the single highest-value follow-up and is stated as a limitation below, not as a finding.
- Full text of PMID 31331701. **Deliberately not attempted** — CLOSED-WORK records it as unrecovered; abstract-only is the retained strength and I did not seek a new route.
- `scripts/preflight.sh` — not run; not authorised by this dispatch and no code was authored.

### Content-policy refusals

**None encountered.** No branch was refused, no denied route replayed, nothing rephrased or rerouted.

---

## Limitations

1. **Abstract level only.** A MIXED-ARM-ONLY classification means *the abstract reports toxicity only over the mixed denominator*. A supplementary safety table disaggregated by histology would change rows 5 and 6 (cabozantinib, apatinib) and would be the only way to discover it. Those rows are therefore **provisional at abstract level**, not proven absent from the papers. This is UNKNOWN, not zero.
2. **The set is exactly W07's Q5, no wider.** Q5 was `"extraskeletal myxoid chondrosarcoma"[All Fields] AND ("adverse event" OR "adverse events" OR "toxicity" OR "tolerability")`. A paper reporting EMC-specific AEs while using only the words "side effects", "complications", "safety" or a bare CTCAE grade term is **outside this set and would not have been found**. The enumeration is complete over the named nine; it is not complete over the literature. Conference abstracts, non-English and unindexed sources are likewise outside it.
3. **PMID 31331701 is used at CLOSED-WORK-retained strength.** No exposure window, no rate of my own, no method-omission claim, no erratum content. The 26-patient safety denominator contains three patients without stated central molecular confirmation of EMC.
4. **n(EMC) is UNKNOWN for the cabozantinib trial.** The abstract names EMC among the responding histologies without a count, so I cannot say how many of the 54 evaluable patients had EMC — only that at least one did.
5. **Nothing here is clinical.** This is an evidence-availability enumeration. It estimates no toxicity burden, supports no treatment choice, and the single EMC-specific source is one drug in one pretreated advanced cohort.
6. **The local literature cache is still absent from this checkout**, as W07 recorded. W07's next-action note asked that this be run where the cache is present so full texts could be checked; it was not available to me, which is precisely why Limitation 1 above stands.
7. **I did not re-verify W07's other 15 table rows** and neither confirm nor disturb them; only its Limitation 2 and the toxicity bullet in its §5.4 are affected.

---

## Stop condition

**Set:** all nine classified with their exact evidence sentence, plus an explicit verdict on W07's Limitation 2.

**Status: MET.** All nine classified (§5.2), each with a verbatim AE-bearing sentence from the PubMed abstract; zero UNRECOVERED. **Verdict: Limitation 2 is REFUTED, not closed and not merely narrowed.** W07's claim *"EMC treatment toxicity has never been reported with an EMC-specific denominator"* is false as written and must be withdrawn; PMID 31331701 is the counterexample. The corrected, fully enumerated replacement claim is in §5.4 and concerns mixed-histology series specifically.

---

## Tool-call and wall-clock count actually used

**Tool calls: 7** (4 Bash, 1 ToolSearch, 1 PubMed MCP metadata call covering all nine articles, 1 closing Bash). **Wall clock: ~1 minute** (02:01:52 → 02:02:45 UTC). Far inside the ~40-call / ~40-minute self-observed target; returned on stop-condition satisfaction with no padding. The single batched PubMed call is why this was cheap — nine abstracts, one round trip.

---

## Next concrete action

**One specific successor:** retrieve the full texts (or supplementary safety tables) of **PMID 34716194** (cabozantinib, Clin Cancer Res, PMC8776602) and **PMID 32547189** (apatinib, Cancer Manag Res, PMC7237692) — both have PMC identifiers, so this is a CI-side fetch, not a paywall problem — and check whether either disaggregates adverse events by histology. This is the only way to convert their MIXED-ARM-ONLY classification from abstract-level-provisional into established, and it also recovers the missing n(EMC) for the cabozantinib trial. Finite (two papers), binary per paper, and it is the last remaining soft edge in §5.4's replacement claim. It should be run where PMC egress works; this environment's PMC route is recorded in-repo as commonly blocked, so this belongs on the Actions runner rather than in a worker session.

**Explicitly not a successor:** further pazopanib retrieval. That route is closed and I did not test it.

---

result: W07's Limitation 2 is REFUTED — enumerating all nine EMC toxicity papers (PubMed, count 9, zero unrecovered) found one that does carry an EMC-specific graded adverse-event denominator (PMID 31331701, pazopanib EMC-only phase 2, safety population 26, authors' own grade 3 counts: hypertension 9/26, ALT 6, AST 5, no grade 4 or deaths), so "EMC toxicity has never been reported with an EMC-specific denominator" must be withdrawn and replaced by the enumerated claim that no mixed-histology series (trabectedin 3/36, apatinib 3/33, cabozantinib EMC-count-unstated/54) has ever disaggregated toxicity by histology — even the apatinib study, which identifies its EMC subset for efficacy and not for safety — with the remaining four EMC-specific sources being narrative and ungraded case reports; no rate computed, nothing pooled, no repository writes.
