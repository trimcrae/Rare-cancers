> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Start `date -u`: `Tue Sep  8 02:34:01 UTC 2026` · End `date -u`: `Tue Sep  8 02:36:05 UTC 2026`

---

# W07d — Is lane 7's nine-paper set stable under vocabulary widening?

## Worker

- **Worker ID:** W07d · **Lane 7 refill** — successor named explicitly by W07c ("Next concrete action"), attacking W07b Limitation 2 / W07c Limitation 4.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I report myself as Claude Opus 5 (`claude-opus-5`) under Claude Code 2.1.42 in a remote cloud environment. I did not observe the served model and do not assert it as fact; the coordinator extracts the actual per-child runtime model from the transcript.
- **HEAD actually read:** `7d081218f107363573573e6d102e4334567adf77` (`git rev-parse HEAD`, exit 0) at both start and end. **This is neither the brief's frozen `92abbcb9…` (W07/W07b) nor W07c's `b9a0257e…`** — the coordinator has committed the collected reports since. `git status --porcelain | grep -c .` → `0` (clean tree) at end.
- **Frozen corpus:** read at `/tmp/claude-0/frozen-corpus/extracted/` (read-only, not overlaid, not copied).
- **`date -u` at start:** `Tue Sep  8 02:34:01 UTC 2026` · **at end:** `Tue Sep  8 02:36:05 UTC 2026`

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (identical set at end; substantive match count 46 at end after filtering the five proxy/`JAVA_TOOL_OPTIONS` lines that match only through embedded `anthropic.com` hostnames):

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

**Write-isolation compliance:** I wrote nothing into the repository. `mkdir -p /tmp/claude-0/w07d/` was created but remained **empty** (`ls -la` → only `.` and `..`); no scratch file was needed because no code was authored and no full text was fetched. All Bash calls were read-only (`date`, `env`, `git rev-parse`, `git status`, `ls`, `cat`, `sed -n`, `wc`, `rg`). No git write operation. `scripts/preflight.sh` not run (not authorised, no code authored).

---

## Question

**Is lane 7's nine-paper set stable under vocabulary widening — and if not, what does the widened set contain?**

Open because every claim W07, W07b and W07c produced is enumerated over a set defined by exactly four search terms (`adverse event` / `adverse events` / `toxicity` / `tolerability`). W07b Limitation 2 and W07c Limitation 4 both state, in the same words, that a paper reporting EMC-specific adverse events under "side effects", "complications", "safety" or a bare CTCAE term would be outside that set and would never have been found. W07c named this the largest remaining soft edge in the lane. Until now the completeness of the nine-paper set had never been tested.

---

## Prior-work check

Commands run read-only from `/home/user/Rare-cancers` (verbatim outputs in Validation evidence):

1. `cat …/opus-capacity-campaign-20260908/COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md` — all three read in full before any other action.
2. `cat …/reports/W07-patient-reported-outcomes-denominators.md` (290 lines), `sed -n` over `W07b-toxicity-denominator-enumeration.md` (266 lines) and `W07c-toxicity-fulltext-resolution.md` (304 lines) — all three transferred reports read, including W07b's rubric definition verbatim, which I reproduce below **unchanged**.
3. `ls …/reports | grep -i W07` — confirms exactly three predecessor reports; no W07d artefact pre-exists.
4. Per-PMID corpus-presence loop over all 17 newly-found PMIDs: `for p in …; do rg -c -- "$p" --glob '!.git' . | wc -l; done` (exit 0). Result in §Result 5.4 — **14 of 17 already appear in the tracked working tree**; three (`21922364`, `20443130`, `15980139`) appear in **zero** tracked files.
5. Per CORPUS-CONTEXT §"How workers must use it", before making any absence claim about those three I checked the frozen corpus: `cd /tmp/claude-0/frozen-corpus/extracted/corpus && rg -l -- "<pmid>" .` → **0 files for each of `21922364`, `20443130`, `15980139`**. Both the live checkout and the frozen selected snapshot lack them. Per the snapshot's own `snapshot-provenance.json` this remains **UNKNOWN, not repository-wide absence.**
6. `rg -n -i "severe diarrhea|dose reduction of pazopanib|Paoluzzi" --glob '!.git' .` → the Paoluzzi 2018 abstract (PMID 30534357), including its dose-reduction sentence, **is already retained verbatim** in `research/literature/rt-lung-mets-probe.json` (lines 648, 835, 1800). **The source is not new to the corpus; only its AE classification is.**

**What is genuinely new here:** not papers, but (a) the measured answer to whether the four-term set is complete, and (b) a per-paper AE-denominator classification for 17 records that no tracked file contains.

**CLOSED-WORK compliance, item by item.** No denied route was replayed. Sunitinib 2014 (`24703573`) — not touched, not returned by either query, no claim made. Wagner 2020 (`32856598`), CTARC 2022 (`35144048`), Trabectedin/RT 2018 (`10.4172/clinical-practice.1000433`) — not touched, not returned. Pazopanib primary `31331701` — appears in both queries as an already-known member of the nine, was **not reclassified and no full text sought**; W07b's abstract-level retained strength stands untouched. Anthracycline `PMC3879193`/`24345066` — not touched, no rate. PUB-EMC-CLASSIFICATION and every Brenca route — not approached. **Zero full-text calls were made in this run**, so the `convert_article_ids`-before-`get_full_text_article` guard had nothing to guard; it is recorded as PROPOSED (NOT RUN) below. **No case was added to any pooled denominator; nothing was pooled at all; no rate was computed.**

---

## Method / inputs

**Retrieval: PubMed MCP only**, `mcp__PubMed__search_articles` ×2 and `mcp__PubMed__get_article_metadata` ×2, executed 2026-09-08 between 02:34 and 02:35 UTC. According to PubMed, all article metadata, abstracts and quoted sentences below come from those calls; a DOI link is given for every article named. **No full-text retrieval, no PMC call, no non-PubMed route, no web fetch.**

**Query W (widened), executed verbatim as returned by the server:**

```
"extraskeletal myxoid chondrosarcoma"[All Fields] AND ("side effect"[All Fields] OR "side effects"[All Fields]
OR "complication"[All Fields] OR "complications"[All Fields] OR "safety"[All Fields] OR "CTCAE"[All Fields]
OR "dose reduction"[All Fields] OR "discontinuation"[All Fields] OR "tolerability"[All Fields]
OR "toxicity"[All Fields])
```

**Deviation from the dispatch string, declared:** the dispatch specified `"side effect*"` and `"complication*"`. The PubMed MCP tool's own contract states the query *"[c]annot … use wildcard symbols like `*`"*. I expanded each truncation into its explicit singular/plural pair rather than dropping it, which is at least as inclusive for these two terms in `[All Fields]`. `query_translation` returned by the server is byte-identical to the query I sent — **no silent term expansion occurred.**

**Query Q5 (W07's original), re-executed unchanged as a control:**

```
"extraskeletal myxoid chondrosarcoma"[All Fields] AND ("adverse event"[All Fields] OR "adverse events"[All Fields]
OR "toxicity"[All Fields] OR "tolerability"[All Fields])
```

**Classification rubric — W07b's, reproduced unchanged and applied without modification:**

- `EMC-SPECIFIC` — an adverse-event statement whose denominator is a set consisting only of EMC patients (any n, including n=1), whether graded counts or a narrative statement about those patients.
- `MIXED-ARM-ONLY` — the paper contains EMC patients and reports adverse events, but only over a denominator that also contains non-EMC patients.
- `NO-AE-DATA` — no adverse-event statement bearing on EMC patients (including: the study contains no EMC patients).
- `UNRECOVERED` — record not retrievable.
- Sub-flag: **graded/counted** (CTCAE-style numerator over denominator) vs **narrative** (unquantified, e.g. "without severe toxicity").

I classified **only** the PMIDs not already among the nine.

---

## Result

### 5.1 Headline — the nine-paper set is **NOT STABLE**. Verdict: **UNSTABLE**

`total_count` for **Q5 = 9**, returning exactly `41476450, 41323055, 36568164, 35494187, 34716194, 32547189, 31509242, 31331701, 23058004` — W07's nine, replicated byte-for-byte seven days on. `total_count` for **Query W = 25**.

**Seventeen PMIDs are new.** Vocabulary widening nearly triples the candidate set.

A second, sharper structural finding: **Query W is not a superset of Q5.** It misses **PMID 34716194** (cabozantinib) — the abstract of which uses only "adverse events", none of the ten widened terms. So neither query contains the other, and **the true union is 26 papers, not 25 and not 9.** Any future lane-7 enumeration must be stated over the union, and no single one of these term lists is safe to use alone.

### 5.2 Classification of the 17 not-already-known PMIDs (rubric unchanged)

According to PubMed. Evidence grade `PRIMARY` = the paper's own reported observation; `UNKNOWN` where the record does not carry the datum. `n(EMC)` as stated by the source; unstated is UNKNOWN, never zero.

| # | PMID | Yr | Journal / design | n(EMC) / total | AE-bearing sentence (verbatim from the PubMed abstract) | Classification | Grade |
|---|---|---|---|---|---|---|---|
| 1 | 39441321 | 2024 | Ann Surg Oncol — case report, laparoscopic-assisted cryoablation, 2 patients | 1 of 2 (other = desmoid) | *"Both patients recovered well without complications and were without radiographic evidence of persistent or recurrent disease at 12 and 18 months postoperatively, respectively."* [DOI](https://doi.org/10.1245/s10434-024-15899-1) | **MIXED-ARM-ONLY** (narrative) — **borderline, flagged**: the statement is universally quantified over 2 patients and so distributes to the EMC patient, but its stated denominator contains a non-EMC patient, which is what the rubric tests. Classified by the rubric as written; the distributive reading is recorded, not adopted | PRIMARY |
| 2 | 38599736 | 2024 | Rev Esp Patol — case report, EMC metastasis to a Meckel's diverticulum adenocarcinoma | 1 of 1 | No treatment-adverse-event statement. Death sentence is disease-attributed: *"the patient had diffuse metastatic pulmonary disease and died eight months later due to disease progression."* [DOI](https://doi.org/10.1016/j.patol.2023.12.002) | **NO-AE-DATA** | UNKNOWN |
| 3 | 34470448 | 2021 | Rev Esp Enferm Dig — anti-Hu paraneoplastic chronic intestinal pseudo-obstruction with EMC | 1 of 1 | Abstract is **truncated to its introduction only** and contains no AE statement; the reported syndrome is a paraneoplastic disease manifestation, not a treatment event. [DOI](https://doi.org/10.17235/reed.2021.8195/2021) | **NO-AE-DATA** at abstract level (truncated abstract — UNKNOWN, not zero) | UNKNOWN |
| 4 | 32948981 | 2020 | Invest New Drugs — **preclinical**, H-EMC-SS xenograft in SCID mice, ICF05016 + external-beam RT | **0 patients** (murine) | *"the HAP strategy potentiated EBR efficacy at a lower dose (6 Gy) by improving survival without generating side effects"* — **the subjects are mice.** [DOI](https://doi.org/10.1007/s10637-020-01002-4) | **NO-AE-DATA** (contains no EMC patients). This is a "side effects" hit that is entirely animal-model, and its safety language must never be read across to any patient | PRIMARY (preclinical) |
| 5 | 31827370 | 2019 | Sarcoma — multicentre retrospective, nanosomal docetaxel lipid suspension in sarcoma | **1 of 11** (*"extraskeletal myxoid chondrosarcoma (EMC) … (9.1% each, 1/11 each)"*; the one EMC patient received NDLS + cyclophosphamide) | *"At least 1 AE was reported in 7 (63.6%) patients. Neutropenia, thrombocytopenia, lymphopenia, and anemia were the hematological AEs, whereas nausea, vomiting, and diarrhea were the most common nonhematological AEs. NDLS treatment was well tolerated without any new safety concerns."* [DOI](https://doi.org/10.1155/2019/3158590) | **MIXED-ARM-ONLY** (counted, over 11 mixed sarcomas) | PRIMARY |
| 6 | **30534357** | 2018 | Clin Sarcoma Res — Paoluzzi & Ghesani, single-patient EMC case report, pazopanib + RT | **1 of 1** | *"Dose reduction of pazopanib due to severe diarrhea was followed by rapid disease progression in the pelvis requiring vascular stenting; increase in tumor growth after discontinuation of a TKI has been described in other malignancies and is a possibility in this specific patient."* [DOI](https://doi.org/10.1186/s13569-018-0108-8) | **EMC-SPECIFIC (n=1, narrative, ungraded)** — the single most consequential new row; see §5.3 | PRIMARY |
| 7 | 29381948 | 2017 | Medicine (Baltimore) — primary cerebellar EMC case report; surgery + adjuvant RT + temozolomide | 1 of 1 | No AE statement; outcome sentence is efficacy only (*"The patient survives with no tumor recurrence… Progression-free survival exceeded 20 months."*). [DOI](https://doi.org/10.1097/MD.0000000000008684) | **NO-AE-DATA** | UNKNOWN |
| 8 | 28852958 | 2017 | Med Oncol — three-centre retrospective, antiangiogenic agents in advanced chondrosarcoma | **1 of 10** (one each: clear cell, extraskeletal mesenchymal, **extraskeletal myxoid**; seven conventional) | *"Antiangiogenic therapy was well tolerated in this series of patients."* [DOI](https://doi.org/10.1007/s12032-017-1030-2) | **MIXED-ARM-ONLY** (narrative, over 10 mixed chondrosarcomas) | PRIMARY |
| 9 | 28187993 | 2017 | J Orthop Sci — case report, EMC with a huge expanding hematoma | UNKNOWN | PubMed returns **`"[Abstract not available]"`**. No AE-bearing sentence is retrievable. [DOI](https://doi.org/10.1016/j.jos.2016.12.011) | **UNRECOVERED** (metadata resolved, abstract absent → AE content UNKNOWN, **not** zero) | UNKNOWN |
| 10 | 22925697 | 2012 | Diagn Pathol — pulmonary EMC presenting with severe anemia | 1 of 1 | The anemia is a **presenting sign that resolved after resection** (*"Two weeks after resection, the anemia was cured"*), not a treatment toxicity. No AE statement. [DOI](https://doi.org/10.1186/1746-1596-7-112) | **NO-AE-DATA** | UNKNOWN |
| 11 | 21922364 | 2011 | Surg Today — presacral **parachordoma** case report | **0 — EMC appears only in a differential-diagnosis list** | *"Resection of the lesion was complicated by intraoperative bleeding and late occurrence of a pelvic abscess"* — in a **parachordoma** patient. [DOI](https://doi.org/10.1007/s00595-010-4480-0) | **NO-AE-DATA** (zero EMC patients). Structurally identical to PMID 31509242 in the original nine: a hit generated by a non-patient mention, whose complications must never be read across to EMC | PRIMARY (non-EMC) |
| 12 | 21547635 | 2011 | Gen Thorac Cardiovasc Surg — EMC with intrathoracic rupture | 1 of 1 | *"Emergency surgery was performed but resulted in rupture of the pleural side of the tumor."* [DOI](https://doi.org/10.1007/s11748-010-0674-z) | **EMC-SPECIFIC (n=1, narrative, ungraded)** — an **intraoperative surgical event**, not a systemic-therapy toxicity; a different kind of harm from every other row in the lane | PRIMARY |
| 13 | 20443130 | 2010 | J Neurooncol — anti-Hu paraneoplastic cerebellar degeneration with myxoid chondrosarcoma; chemo + IVIG + hydrocortisone | 1 of 1 | No AE statement; the only outcome sentence is benefit (*"marked improvement within 1 week"*). [DOI](https://doi.org/10.1007/s11060-010-0216-7) | **NO-AE-DATA** | UNKNOWN |
| 14 | 18568733 | 2008 | Br J Neurosurg — cerebellopontine-angle EMC presenting in a 20-week pregnancy | 1 of 1 | Abstract refers only to *"the issues associated with management of this tumour"*; no AE statement. [DOI](https://doi.org/10.1080/02688690701780127) | **NO-AE-DATA** | UNKNOWN |
| 15 | 18235511 | 2008 | J Perinatol — congenital high-grade sarcoma, neonate, t(9;22) *"suggestive of a more indolent extraskeletal myxoid chondrosarcoma"* | UNKNOWN — EMC is inferred from cytogenetics, not stated as a confirmed diagnosis | *"Despite attempts to control rapid growth of lesions using high-dose steroids and cis-retinoic acid, patient's clinical status continued to deteriorate"* — deterioration is **disease-attributed**, not treatment-attributed. [DOI](https://doi.org/10.1038/sj.jp.7211890) | **NO-AE-DATA** | UNKNOWN |
| 16 | 15980139 | 2005 | Vet Rec — *"Extraskeletal myxoid chondrosarcoma in a cow."* | **0 human patients (bovine)** | PubMed returns `"[Abstract not available]"`. [DOI](https://doi.org/10.1136/vr.156.26.842) | **NO-AE-DATA** (veterinary; contains no patient and can contribute no human EMC AE denominator under any reading of the abstract). Abstract absence recorded | UNKNOWN |
| 17 | 10450885 | 1999 | Skeletal Radiol — knee EMC, multiply recurrent, surgery + chemotherapy | 1 of 1 | *"At 64 months, the patient died from complications of extraskeletal myxoid chondrosarcoma"* — **complications of the disease**, explicitly, not of treatment. [DOI](https://doi.org/10.1007/s002560050531) | **NO-AE-DATA** | UNKNOWN |

**Tally over the 17 new PMIDs:** `EMC-SPECIFIC` **2** (graded/counted **0**, narrative **2**) · `MIXED-ARM-ONLY` **3** (counted 1, narrative 2) · `NO-AE-DATA` **11** · `UNRECOVERED` **1**.

**Tally over the full 26-paper union** (W07b's nine, unchanged by me, plus these 17): `EMC-SPECIFIC` **7** (graded/counted **1**, narrative **6**) · `MIXED-ARM-ONLY` **6** · `NO-AE-DATA` **12** · `UNRECOVERED` **1**.

### 5.3 What the widening changes, and what it does not

**Does not change — the load-bearing claim survives.** Widening added **zero** graded, counted, EMC-specific adverse-event denominators. W07b's central statement holds and is now enumerated over 26 papers instead of 9:

> *"Graded, denominator-bearing EMC-specific safety data exist in exactly one study in this set — the pazopanib EMC phase 2 trial (PMID 31331701, safety population 26) — and nowhere else."*

That is a materially stronger claim than it was this morning, because the set it quantifies over was tripled by an adversarial vocabulary and the exception count stayed at one.

**Does change — three things.**

1. **The set's definition is now known to be fragile in both directions.** Nine was not the number; 26 is the number under two term lists, and each list misses papers the other catches. Every lane-7 sentence beginning "in this set" must name the union and its two queries.
2. **A second EMC-specific dose-reduction record now exists, and it was invisible to Q5.** PMID 30534357 records, for one EMC patient, a **pazopanib dose reduction for severe diarrhea**. This is exactly the vocabulary W07b Limitation 2 predicted would be missed — the word "toxicity" never appears; "dose reduction" and "discontinuation" do. The prediction was correct. Note carefully: this is **narrative and ungraded** ("severe diarrhea" is not a stated CTCAE grade), it is **n=1**, it is a **different paper** from the pazopanib trial, and it is **not** the denied `31331701` route. **It is one patient, not a rate. There is no denominator here beyond 1, and none may be constructed.**
3. **The efficacy/safety asymmetry W07c demonstrated at 3 of 3 now stands at 6 of 6.** Every mixed-histology paper in the union that reports adverse events reports them only over the mixed denominator: trabectedin (3 EMC of 36), apatinib (3 of 33), cabozantinib (3 of 54), NDLS docetaxel (1 of 11), antiangiogenic chondrosarcoma (1 of 10), cryoablation (1 of 2). **No paper anywhere in the union disaggregates its toxicity by histology.** The three new ones were not full-text checked, so their rows are abstract-level-provisional exactly as W07b's were before W07c.

**A fourth observation the widening produced for free:** the widened vocabulary is *noisier*, not merely wider. Of 17 new hits, **11 are NO-AE-DATA**, and three of those are hits for structural reasons that have nothing to do with EMC toxicity — a **mouse xenograft** (32948981), a **parachordoma** case where EMC appears only in a differential list (21922364), and a **cow** (15980139). The word "complications" in particular attaches, in this literature, far more often to *disease* complications (rows 2, 17) and *presenting* signs (row 10) than to treatment harm. A future worker widening further should expect precision to fall faster than recall rises.

### 5.4 Corpus-presence check of the 17 (`rg -c`, live tree at HEAD `7d08121…`)

| Tracked-file hits | PMIDs |
|---|---|
| ≥1 (already in the working tree) | 39441321 (3), 38599736 (2), 34470448 (1), 32948981 (9), 31827370 (2), 30534357 (6), 29381948 (3), 28852958 (3), 28187993 (1), 22925697 (2), 21547635 (3), 18568733 (1), 18235511 (1), 10450885 (5) — **14 of 17** |
| **0** in the live tree **and 0** in the frozen corpus | **21922364, 20443130, 15980139** — 3 of 17 |

None of the 17 is a new *source* to the programme except possibly those three, and per `snapshot-provenance.json` their absence from a selected snapshot is **UNKNOWN, not repository-wide absence**. What is new is the classification, not the citations — and all three of the tree-absent records are `NO-AE-DATA` (a parachordoma paper with no EMC patients, a paraneoplastic case with no AE statement, and a cow), so nothing of lane-7 value hinges on them.

### 5.5 W07c's two source-internal discrepancies — does the widened set touch the same papers?

**Asked and answered, without re-adjudication.**

- **Apatinib, PMID 32547189** — **YES, touched.** It is returned by Query W as well as by Q5 (it uses "safety" and "toxicity"). But it is **already among the nine**, so under my dispatch I did **not** reclassify it, did not re-read it, and do not re-adjudicate the abstract-vs-body discrepancy W07c recorded. Its W07c classification (`MIXED-ARM-ONLY`, confirmed at full-text level) stands untouched.
- **Cabozantinib, PMID 34716194** — **NOT touched, and notably so:** it is **absent from Query W entirely**, because its abstract uses only "adverse events". The paper whose abstract percentages W07c found to disagree with its own Table 3 is the single paper the widened vocabulary drops. That is a coincidence of wording, not a finding about the paper — but it is precisely why §5.1's "neither query is a superset" point matters operationally.

I add nothing to and subtract nothing from W07c §5.4. Neither discrepancy is re-examined, reconciled, or recomputed.

### 5.6 No clinical claim whatsoever — stated explicitly

**Nothing in this lane, and nothing in this report, bears on the safety, tolerability, therapeutic window, efficacy or clinical readiness of pazopanib, cabozantinib, apatinib, trabectedin, sunitinib, docetaxel, any antiangiogenic agent, cryoablation, radiotherapy, any anthracycline, or any other agent or procedure, for any patient.** This is an evidence-availability and search-completeness audit of how a literature reports its numbers. It supports no treatment choice and no comparison between treatments. A toxicity rate without a stated denominator is not a rate: I computed none, carried none forward, imputed no denominator, substituted no nearby cohort `n`, added no case to any pooled denominator, and pooled nothing with anything.

---

## Validation evidence

### RUN

**V1.** Start clock, HEAD, environment.
```
$ date -u
Tue Sep  8 02:34:01 UTC 2026
$ git rev-parse HEAD
7d081218f107363573573e6d102e4334567adf77
```
Exit 0. HEAD divergence from the brief's `92abbcb9…` and from W07c's `b9a0257e…` recorded in §Worker.

**V2.** Query W — `mcp__PubMed__search_articles`, verbatim server response (truncated to the data fields):
```
"pmids":["41476450","41323055","39441321","38599736","36568164","35494187","34470448","32948981",
         "32547189","31827370","31509242","31331701","30534357","29381948","28852958","28187993",
         "23058004","22925697","21922364","21547635","20443130","18568733","18235511","15980139","10450885"],
"total_count":25,"returned_count":25,
"query_translation":"\"extraskeletal myxoid chondrosarcoma\"[All Fields] AND (\"side effect\"[All Fields] OR
 \"side effects\"[All Fields] OR \"complication\"[All Fields] OR \"complications\"[All Fields] OR
 \"safety\"[All Fields] OR \"CTCAE\"[All Fields] OR \"dose reduction\"[All Fields] OR
 \"discontinuation\"[All Fields] OR \"tolerability\"[All Fields] OR \"toxicity\"[All Fields])",
"has_more":false
```
`query_translation` is byte-identical to the submitted query — **no MeSH explosion, no term expansion.** `has_more:false` confirms all 25 returned.

**V3.** Q5 control — same tool, unchanged W07 query, verbatim:
```
"pmids":["41476450","41323055","36568164","35494187","34716194","32547189","31509242","31331701","23058004"],
"total_count":9,"returned_count":9,"has_more":false
```
**Exactly W07's nine, in the same order.** The control reproduces; the widening result is therefore a difference in vocabulary, not in database state.

**V4.** Set arithmetic performed by inspection of V2 and V3: `|Q5| = 9`, `|W| = 25`, `|W \ Q5| = 17`, `|Q5 \ W| = 1` (**34716194**), `|Q5 ∪ W| = 26`, `|Q5 ∩ W| = 8`.

**V5.** Metadata retrieval — two `mcp__PubMed__get_article_metadata` calls covering all 17 new PMIDs (9 + 8). Server returned `"count":9` and `"count":8` respectively; **17 of 17 records resolved**. Every sentence quoted in §5.2 is a verbatim substring of an abstract returned by those two calls, except rows 9 and 16, where the returned abstract field is the literal string `[Abstract not available]` — quoted as such and classified accordingly. **No PMID mismatch was possible to introduce and none occurred**: `get_article_metadata` echoes `identifiers.pmid` per article, and each echoed PMID equals a PMID I requested; the returned set of PMIDs equals the requested set exactly, with nothing extra and nothing missing. Nothing discarded.

**V6.** Corpus-presence loop, verbatim output (exit 0):
```
39441321 tracked_files=3     38599736 tracked_files=2     34470448 tracked_files=1
32948981 tracked_files=9     31827370 tracked_files=2     30534357 tracked_files=6
29381948 tracked_files=3     28852958 tracked_files=3     28187993 tracked_files=1
22925697 tracked_files=2     21922364 tracked_files=0     21547635 tracked_files=3
20443130 tracked_files=0     18568733 tracked_files=1     18235511 tracked_files=1
15980139 tracked_files=0     10450885 tracked_files=5
EXIT=0
```

**V7.** Frozen-corpus check of the three tree-absent PMIDs plus three controls, verbatim (exit 0):
```
21922364 frozen_corpus_files=0    20443130 frozen_corpus_files=0    15980139 frozen_corpus_files=0
31827370 frozen_corpus_files=2    28852958 frozen_corpus_files=3    30534357 frozen_corpus_files=4
```
The three non-zero controls confirm the corpus was actually searched and is not systematically empty for this literature.

**V8.** Paoluzzi retention check (exit 0): `rg -n -i "severe diarrhea|dose reduction of pazopanib|Paoluzzi"` returned three hits, all in `research/literature/rt-lung-mets-probe.json` (lines 648, 835, 1800), each holding the complete PMID 30534357 abstract including the dose-reduction sentence. **The source was already retained; only its EMC-SPECIFIC AE classification is new.**

**V9.** End clock, HEAD, write isolation:
```
$ date -u
Tue Sep  8 02:36:05 UTC 2026
$ git rev-parse HEAD
7d081218f107363573573e6d102e4334567adf77
$ git status --porcelain | grep -c .
0
$ ls -la /tmp/claude-0/w07d/
total 8
drwxr-xr-x  2 root root 4096 Sep  8 02:34 .
drwx------ 82 root root 4096 Sep  8 02:36 ..
```
Exit 0. HEAD unchanged across the run; **working tree clean — zero modifications, mine or anyone's**; my scratch directory is empty. Substantive `env` match count 46 at end, identical set to start.

### PROPOSED (NOT RUN)

- **`mcp__PubMed__convert_article_ids` + `get_full_text_article` for the three new MIXED-ARM-ONLY rows** (31827370 → PMC6881752, 28852958 → PMC5574947, 39441321 → no PMC listed) to check for a histology-disaggregated safety table, exactly as W07c did for cabozantinib and apatinib. **Not run** — outside this dispatch's abstract-level scope. Their MIXED-ARM-ONLY classification is therefore abstract-level-provisional, not full-text-established. Had I run it, the PMCID would have been confirmed via `convert_article_ids` **first** and every returned PMID checked against the requested PMID, per the dispatch's mismatch guard.
- **Recovery of PMID 28187993's missing abstract** (J Orthop Sci; publisher route). Not attempted — no new route was opened and none is authorised here. It stays `UNRECOVERED`.
- **A third widening round** (e.g. `"grade 3"`, `"grade 4"`, `"treatment-related"`, `"morbidity"`, `"withdrawal"`, `"interruption"`, non-English terms). Not run; carried forward as the next action with an explicit precision warning from §5.3.
- **Any pazopanib full-text or erratum retrieval** (31331701). Deliberately not attempted — CLOSED-WORK route, excluded by W07b and W07c, and untested by me.
- `scripts/preflight.sh` — not run; not authorised by this dispatch and no code was authored.

### Content-policy refusals

**None encountered.** No branch was refused, no denied route replayed, nothing rephrased, rerouted or relabelled.

---

## Limitations

1. **Two term lists are still not the literature.** 26 papers is the union of ten widened terms and four original terms, in `[All Fields]`, in English-indexed PubMed. A paper reporting EMC-specific adverse events under vocabulary neither list contains — "grade 3", "treatment-related", "morbidity", "withdrawal", "interruption" — remains outside. The completeness question is **narrowed, not closed.** UNKNOWN, not zero.
2. **The dispatch's wildcards could not be executed as given.** The MCP tool forbids `*`; I substituted explicit singular/plural pairs for `side effect*` and `complication*`. For these two terms in `[All Fields]` that is at least as inclusive, but it is a deviation and it is possible some rarer inflection was lost.
3. **All 17 new classifications are abstract-level only.** No full text was retrieved in this run. The three new MIXED-ARM-ONLY rows carry exactly the provisional status W07b's cabozantinib and apatinib rows carried before W07c resolved them; a supplementary safety table could overturn any of them.
4. **Row 1 (cryoablation, 39441321) is a genuine rubric-boundary case** and I have flagged rather than resolved it. A "both patients" statement over an EMC patient and a desmoid patient distributes logically to the EMC patient while its stated denominator is mixed. I applied the rubric as written and **did not modify it**; a reader who disagrees should reclassify that one row and adjust the tallies by one, which changes no conclusion in §5.3.
5. **Row 9 is UNRECOVERED and row 16's abstract is likewise absent.** PubMed returns `[Abstract not available]` for both. Row 16 is classified NO-AE-DATA on the independent ground that a bovine case contributes no human patient denominator under any reading; row 9 is left UNRECOVERED. Neither is evidence of absence.
6. **Rows 3 and 15 rest on partial or inferential source statements** — a truncated abstract, and a neonatal sarcoma whose EMC status is inferred from a t(9;22) rather than stated as confirmed. Both are recorded as UNKNOWN where the source is silent.
7. **I did not re-verify any of W07's 16 table rows, W07b's nine classifications, or W07c's two full-text verdicts**, and I neither confirm nor disturb them. Only the *scope* of the enumerated set is affected. The pazopanib EMC-specific counterexample stands untouched and unre-checked by me.
8. **HEAD divergence.** I read `7d081218…`, the third distinct HEAD across the four lane-7 runs. External PubMed findings are unaffected; a prior-work `rg` at a different commit could in principle differ, though the only tree changes are the coordinator's collected reports.
9. **Nothing here is clinical**, per §5.6, which is part of the finding and not boilerplate.

---

## Stop condition

**Set (by the dispatch):** the widened query executed, every not-already-known PMID classified under the unchanged rubric, and an explicit verdict on whether the nine-paper set is stable.

**Status: MET, all three parts.**
1. **Widened query executed** — `total_count` 25, `query_translation` unexpanded, V2.
2. **Every not-already-known PMID classified** — all 17, under W07b's four-way rubric reproduced verbatim and **not modified**, each with its evidence sentence or an explicit statement that none exists; 17 of 17 metadata records resolved, 1 classified UNRECOVERED for an absent abstract.
3. **Explicit verdict: the nine-paper set is NOT STABLE.** Widening adds 17 papers (union = 26), and the widened query is not even a superset of the original — it drops cabozantinib. However, the widening added **zero** new graded/counted EMC-specific adverse-event denominators, so W07b's load-bearing claim survives and is now enumerated over 26 papers rather than 9. Two new EMC-specific but **narrative, ungraded, n=1** records were found (a pazopanib dose reduction for severe diarrhea, PMID 30534357; an intraoperative tumour rupture, PMID 21547635), and the efficacy/safety disaggregation asymmetry strengthens from 3 of 3 to **6 of 6**.

Returned on satisfaction, no padding.

---

## Tool-call and wall-clock count actually used

**Tool calls: 19** — 13 Bash (all read-only; one `mkdir` that produced an empty scratch dir), 1 ToolSearch, 2 `mcp__PubMed__search_articles`, 2 `mcp__PubMed__get_article_metadata` (17 abstracts in two round trips), plus the paired setup calls counted among the Bash total. **Zero full-text calls, zero non-PubMed routes.** **Wall clock: ~2.1 minutes** (02:34:01 → 02:36:05 UTC). Well inside the ~40-call / ~40-minute self-observed target.

---

## Next concrete action

**One specific successor:** full-text-resolve the **three new `MIXED-ARM-ONLY` rows** the way W07c resolved the previous two — `mcp__PubMed__convert_article_ids` for PMIDs 31827370 and 28852958 (expected PMC6881752 and PMC5574947; **confirm, do not assume**), then `get_full_text_article` on the confirmed PMCIDs with the returned-PMID mismatch guard applied, and check whether either disaggregates adverse events by histology for its single EMC patient. PMID 39441321 has no PMC id in its metadata and should be left at abstract level rather than routed elsewhere. This is finite (two papers), binary per paper, replays no denied route, and it is what converts "**6 of 6** mixed-histology papers never disaggregate toxicity by histology" from half-established into fully established — currently three of those six rest on abstracts alone.

**Explicitly not successors:** (a) any further pazopanib retrieval — CLOSED-WORK, untested by me and to stay that way; (b) re-adjudicating W07c's two numeric discrepancies; (c) a third vocabulary-widening round *before* the three provisional rows are resolved — §5.3 shows precision is already falling faster than recall is rising (11 of 17 new hits were NO-AE-DATA, three of them a mouse, a parachordoma and a cow), so more terms would add noise ahead of signal; (d) constructing any denominator, rate or pooled figure from anything in this report, which the lane exists to prevent.

---

**result:** Lane 7's nine-paper set is **NOT stable** — widening the vocabulary (PubMed MCP only, `total_count` 25 vs the Q5 control's 9, which replicated exactly) adds **17 new PMIDs**, and the widened query is not even a superset since it drops cabozantinib (34716194), making the true union **26 papers, not 9**; all 17 were classified under W07b's unchanged rubric (EMC-SPECIFIC 2, both narrative/ungraded n=1; MIXED-ARM-ONLY 3; NO-AE-DATA 11; UNRECOVERED 1), and critically the widening added **zero** new graded-and-counted EMC-specific adverse-event denominators, so W07b's claim that exactly one such study exists survives and is now enumerated over 26 papers instead of 9 — while the efficacy/safety asymmetry strengthens from 3 of 3 to **6 of 6** mixed-histology papers that disaggregate efficacy by histology and never disaggregate toxicity; the two new EMC-specific records are a pazopanib **dose reduction for severe diarrhea** in one patient (PMID 30534357, already retained in `rt-lung-mets-probe.json`, and exactly the "dose reduction"/"discontinuation" vocabulary W07b predicted Q5 would miss) and an intraoperative tumour rupture in one patient (PMID 21547635); of W07c's two discrepancy papers the widened set touches apatinib (already among the nine, not reclassified, not re-adjudicated) and **misses cabozantinib entirely**; no full text fetched, no denied route replayed, no rate computed, no denominator imputed, nothing pooled, **no clinical claim of any kind**, and no repository writes — HEAD read was `7d081218f107363573573e6d102e4334567adf77` with a clean working tree at end.
