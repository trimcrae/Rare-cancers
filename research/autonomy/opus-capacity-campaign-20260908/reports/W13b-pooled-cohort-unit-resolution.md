> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

All evidence gathered. Writing the report.

## Worker

**W13b** — refill for lane 13: resolve the unit of `n` for the five pooled cohorts and the three Meis-Kindblom denominators. This is W13's own named successor.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the runtime model from the transcript. I do not assert it as observed fact.

`date -u` at start: `Tue Sep  8 02:06:51 UTC 2026`. `date -u` at end: `Tue Sep  8 02:12:23 UTC 2026`.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (proxy-list and `JAVA_TOOL_OPTIONS` lines filtered by me for length — they match only on the `anthropic` substring inside `no_proxy` and carry no model identity):

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

⚠ **Frozen-commit correction, reported not concealed.** `git rev-parse HEAD` returned `92abbcb905cacf07f14b238db50d1b98f6590374` (the brief's frozen commit) at 02:06:51Z and `103ff76f1d66426420c56a4d49752eb84f5f5c39` at 02:11:56Z — the coordinator committed `103ff76f "Add OPUS-CAPACITY-CAMPAIGN-20260908 manifest and worker reports"` mid-run. I verified my two input files are unaffected: `git diff --stat 92abbcb HEAD -- research/data/emc-clinical-registry.json research/modalities/emc-fourth-cohort-quant.json` is **empty** — byte-identical. Nothing in this report is invalidated. That commit does have a separate live consequence for W13's validator, quantified in Validation evidence below.

**Write isolation honoured.** `git status --porcelain`, filtered to exclude other workers' untracked files, is **empty**. I wrote nothing under `/home/user/Rare-cancers` and ran no git write operation against it. All execution was in `/tmp/claude-0/w13b/`.

## Question

**For the five cohorts that actually feed the pooled headline (`registry.cohorts[0..4]`), what does each source's own sentence say its headline count counts — patients, tumours, or specimens — and what explains the three Meis-Kindblom denominators (83, 76, 99) that differ from its `n=117`?**

It is open because W13 proved by machine check (C1, 14/14) that no committed file states the unit of any cohort `n`, and closed its report with the explicit finding that each of the 14 is **UNKNOWN until read, not "probably patients"**. W13 could not resolve it because it made no external retrieval.

## Prior-work check

Commands actually run:

- `rg -n "nUnit|denomNote|n_unit|unit of n" --glob '!.git'` — **no hit anywhere in the tree** proposes or uses either field. Every `unit`/`n_units` hit is molecular-dynamics or image-resolution (`results/nr4a3-step1-fanout/results/_map.json`, `research/manuscripts/figures/svg_to_print_formats.py`, `research/modalities/nr4a3_md_release.py`). The two fields are genuinely new.
- `rg -ln "emc-clinical-registry" --glob '!.git'` — 20 files reference the registry; `systems/POLICY-evidence.md` and `scripts/validate-registry.mjs` are the governing pair.
- `sed -n '110,200p' systems/POLICY-evidence.md` — read §2.1 through §2.6 in full to establish what the headline arithmetic actually consumes.
- Python enumeration of `registry.cohorts` confirming that the `pool: true` set is **exactly `cohorts[0..4]`** and no other row — so these five rows are the entire pooled headline, not a sample of it.

`CLOSED-WORK.md` read in full. **Denied routes I did not replay:** Meis-Kindblom 1999 full text (paywalled, `openAccess: false` in the registry's own citation) — I retrieved **only the PubMed abstract record**, which is a permitted route and is what the repository already holds; I made no attempt at the publisher, no PDF fetch, no proxy route. The **pazopanib** primary (unrecovered) is not among my five rows and I did not touch it; W13's A3/A4 findings about it stand untouched and unresolved. USSC 2022 (`ussc2022`, PMID 35962783) is **not** the CTARC 2022 record (PMID 35144048) named in CLOSED-WORK — different papers; I used its PubMed abstract only, which required no publisher route. I did not reopen Brenca, Hofvander, Wagner, sunitinib, trabectedin/RT, or SEER.

## Method / inputs

Read-only inspection of the working tree; scratch execution in `/tmp/claude-0/w13b/`. Python 3.11.15, Node (for the incumbent gate), Linux 6.18.44-fc-v24. No paid API, no GPU, no writes to the repository.

Repository inputs: `research/data/emc-clinical-registry.json` (14 cohorts, 25 citations, 4 patients); `systems/POLICY-evidence.md` §2.1–§2.6; `scripts/validate-registry.mjs`; W13's report (validator source extracted verbatim by regex, 196 lines, so no transcription drift).

**External retrieval — 3 calls, all via the PubMed MCP server.** According to PubMed:

- `get_article_metadata(["10366145","35962783","32612944"])` → Meis-Kindblom 1999, [DOI](https://doi.org/10.1097/00000478-199906000-00002); Gusho 2022, [DOI](https://doi.org/10.1002/jso.27062); Chiusole 2020, [DOI](https://doi.org/10.3389/fonc.2020.00828).
- `get_full_text_article(["PMC12398172"])` → Masunaga 2025, [DOI](https://doi.org/10.1186/s13018-025-06245-6) (CC-BY, open access).
- `get_full_text_article(["PMC7308468"])` → Chiusole 2020, [DOI](https://doi.org/10.3389/fonc.2020.00828) (CC-BY, open access).

No content-policy refusal was encountered in this lane. No 403 was encountered, because I attempted no publisher route.

## Result

### 1 · The five rows I am resolving, and what each currently claims

| # | `label` | `n` | `sourceId` | citation `openAccess` | pooled outcomes it feeds (`events/denom`) |
|---|---|---|---|---|---|
| `cohorts[0]` | Localised at diagnosis, surgically treated | 134 | `masunaga2025` | true (PMC12398172) | recurrence 16/134, metastasis 39/134, diseaseDeath 9/134 |
| `cohorts[1]` | Metastatic at diagnosis | 29 | `masunaga2025` | true (PMC12398172) | diseaseDeath 9/29 |
| `cohorts[2]` | Long-term outcome series (Meis-Kindblom) | 117 | `meisKindblom1999` | **false** | recurrence 40/**83**, metastasis 35/**76**, diseaseDeath 18/**99** |
| `cohorts[3]` | US Sarcoma Collaborative database | 60 | `ussc2022` | **false** | recurrence 18/60 |
| `cohorts[4]` | European two-institution series (Chiusole) | 49 | `chiusole2020` | true (PMC7308468) | recurrence 14/49, metastasis 20/49 |

None of the five carries `primaryRef`; all five are `provenance: "primary"`, so W13's A3/A4 pazopanib problem does not touch this set. `cohorts[0]` and `cohorts[1]` share `populationKey: "masunaga2025-jpreg"` with distinct `stratum` values — legal under §2.3, and I confirm from the source that the two strata are mutually exclusive (142 without metastases minus 8 non-surgical = 134; plus 29 with = 163 of the study's 171).

### 2 · Per-row unit verdict, from the source's own sentence

| row | verdict | class | the source's own sentence |
|---|---|---|---|
| `cohorts[0]` n=134 | **patient** | **PRIMARY (stated)** | Masunaga 2025, Results: *"For the prognostic analysis, eight patients who did not undergo surgery were excluded, and the remaining **134 patients** were included."* The same paragraph states all three committed event counts in the same unit: *"Local recurrence occurred in **16 patients** (11.9%)"*, *"Distant metastases occurred in **39 patients** (29.1%)"*, *"**Nine patients** (6.7%) died due to the tumor"*. |
| `cohorts[1]` n=29 | **patient** | **PRIMARY (stated)** | Masunaga 2025, Results: *"A total of **29 patients** had distant metastases at the time of diagnosis."* The committed 9/29 disease deaths is the sum of two disjoint sub-groups both stated in patients: *"Among the 16 patients who received advanced-stage chemotherapy… **five (31.3%) died of the tumors**"* and *"Among the 13 patients who did not receive advanced-stage chemotherapy, nine (69.2%) survived with tumors, and **four (30.8%) died of tumors**."* |
| `cohorts[2]` n=117 | ⛔ **UNKNOWN** | **UNKNOWN** | The source's own word is **"cases"**, and it never equates cases to patients. Meis-Kindblom 1999 abstract: *"The clinical, morphologic, and immunohistochemical features of **117 previously unreported cases** were studied and statistically analyzed."* Title likewise: *"…based on 117 cases."* |
| `cohorts[3]` n=60 | **patient** | **PRIMARY (stated)** | Gusho 2022 abstract, Methods: *"**EMC patients** were identified from the United States Sarcoma Collaborative database between 2000 and 2016."* Results: *"**Sixty individuals** with a mean age of 55 years were included, and 65.0% (n = 39) were male."* The committed 18/60 is verbatim: *"The locoregional recurrence rate was 30.0% (**n = 18/60**)."* |
| `cohorts[4]` n=49 | **patient** | **PRIMARY (stated)** | Chiusole 2020, Results: *"Out of **49 patients** treated with curative intent, **20 patients** (40.8%) developed metastases and **14 patients** (28.6%) developed local recurrence."* |

**Why `cohorts[2]` is UNKNOWN and not "probably patients".** The abstract does attach patient-level attributes to the same 117-set — *"The median **patient** age was 52 years (range, 6-89 years)"* and *"The male-to-female ratio was 2:1"* — which is **consistent with** one case = one patient but does not state it. This is precisely the reading W13 forbade. The concrete failure mode is live here rather than theoretical: the registry's own note records *"Consultation cases (selection toward difficult tumours)"*, and a consultation/referral pathology series accessions **cases**, so one patient's primary and their later recurrence can arrive as two cases. I therefore record UNKNOWN.

⚠ **One secondary attestation exists and I am recording it as insufficient, not as the answer.** Chiusole 2020's Discussion describes the same study as *"a retrospective series of **117 patients** with EMC treated with surgery as primary intent, a rate of 48% of local recurrence and 46% of metastatic recurrence was reported"*. That is a third party's word, not the source's own sentence, and the brief's standard is the source's own words. It also demonstrably misdescribes the design — Meis-Kindblom's series is not "treated with surgery as primary intent" in the way Chiusole implies, and Chiusole attaches the 48%/46% rates to the 117 rather than to their real denominators of 83 and 76. A secondary source that gets the denominator wrong is not evidence about the unit.

The only route that would settle it is the Meis-Kindblom full text, which is **paywalled** (`openAccess: false` in the repository's own citation entry) and recorded unrecovered in `CLOSED-WORK.md`. I did not attempt it. **UNKNOWN is the complete and honest result for this row.**

### 3 · The three Meis-Kindblom denominators

| denominator | unit | gap explained? | the source's own sentence |
|---|---|---|---|
| `diseaseDeath.denom = 99` | **"cases"** (the source's word) | ✅ **YES — missing follow-up data.** | *"Follow-up information was available in **99 cases** (median, 9 years: range, 2 months-22 years)."* The 117→99 gap is absence of follow-up, not a different unit and not a sub-stratum. |
| `recurrence.denom = 83` | **patient (stated)** | ⛔ **UNKNOWN** | *"There were local recurrences in 40 (48%) of **83 patients**, 23 (58%) of whom had multiple local recurrences."* 40/83 = 48.2%, matching the stated 48% — events and denom are read verbatim. The abstract nowhere says why 83 rather than 99 or 117. |
| `metastasis.denom = 76` | **patient (stated)** | ⛔ **UNKNOWN** | *"Metastases occurred in 35 (46%) of **76 patients**."* 35/76 = 46.1%, matching the stated 46%. The abstract nowhere says why 76, does not describe it as a stratum, and does not state its relation to 83 or 99. |

**Direct answer to "missing data, a different unit, or a sub-stratum?"**

- For **99**: missing data. Stated.
- For **83 and 76**: **not a different unit** — both are stated in patients, which positively rules out one of the three hypotheses. Between *missing data* and *sub-stratum* the abstract does not choose, and both remain consistent with it. UNKNOWN, full text unrecoverable on a permitted route.
- A fourth fact the abstract does establish and that the registry does not record: **83 and 76 are not stated to be nested or disjoint**, so `cohorts[2]` contributes a *different population* to each of the three pooled outcomes.

⚠ **A unit seam inside one row.** For disease death this row's **numerator is stated in patients** — *"Forty-eight patients were disease-free, and 41 patients had evidence of disease (**18 of these had died of disease**). Ten additional patients survived, but their disease status was unknown."* — while its **denominator is stated in cases** (the 99). The committed `18/99` therefore has a numerator and a denominator expressed in different unit words *by the source itself*. That is not an error the repository introduced; it is one the repository silently inherited and never recorded.

### 4 · One incidental finding, positive

Chiusole's abstract gives only percentages (28.6%, 40.8%), and `POLICY-evidence.md` §2.1(2) forbids deriving counts from a published percentage for pooling because "rounding invents data". 28.6% × 49 = 14.01 and 40.8% × 49 = 19.99, so the committed events 14 and 20 *look* reconstructed. **They are not.** The full text states the integers directly: *"20 patients (40.8%) developed metastases and 14 patients (28.6%) developed local recurrence."* `cohorts[4]` complies with §2.1(2). I checked this because it would have been a real violation; it is not one, and I record the clearance rather than only recording defects.

### 5 · A finding outside my task that I am reporting rather than acting on

The registry's citation `meisKindblom1999` records `"population": "117 EMC cases (**AFIP**), median follow-up 9 yr"`. The PubMed record's first-author affiliation is *"Gothenburg Musculoskeletal Tumor Center, Sahlgren University Hospital, Department of Pathology, Gothenburg University, **Sweden**."* The retrieved record does not support "AFIP". This is **UNKNOWN**, not refuted — Meis-Kindblom's earlier career was at AFIP and the case material's provenance is not stated in the abstract — but the parenthetical is currently unsourced. It belongs to the registry owner; it is not part of my patch, because guessing at it would be exactly the error this lane exists to prevent.

## Validation evidence

Environment for every run below: Linux 6.18.44-fc-v24, Python 3.11.15, cwd as noted, exit codes as returned by the shell.

### RUN 1 — W13's validator reproduced against the frozen checkout

Validator source extracted verbatim from W13's report by regex (196 lines, matching W13's stated 196) — no retyping.

```
$ python3 /tmp/claude-0/w13b/validate_identity_contract.py /home/user/Rare-cancers
...
TOTAL FINDINGS: 42 across 3 files (41 violations, 1 annotated guards)
REAL_EXIT=1
```

W13's headline reproduced exactly at HEAD `92abbcb`: 42 findings, 41 machine violations + 1 annotated guard, exit 1.

### RUN 2 — scratch mirror, calibrated to byte-identity before any patch was measured

I cannot swap a file inside the repository, so I built a scratch mirror at `/tmp/claude-0/w13b/mirror` from `git ls-files '*.md' '*.json'` (5,086 paths; `comm` against the real list shows **zero** files in either direction only). First attempt gave **50 findings across 6 files** — 8 more than the real repo.

⚠ **I diagnosed this before trusting any delta rather than accepting the convenient number.** The 8 extras are C12/C12b hits on the campaign's *own* reports (`W01b`, `W05`, `W13`), which were **untracked** in the real repo at `92abbcb` and which my `git add -A` made tracked. That is exactly the false-positive class W13 fixed by restricting C12 to `git ls-files`. Removing that directory from the mirror:

```
$ python3 /tmp/claude-0/w13b/validate_identity_contract.py /tmp/claude-0/w13b/mirror
TOTAL FINDINGS: 42 across 3 files (41 violations, 1 annotated guards)
REAL_EXIT=1
$ diff runA.txt runB2.txt && echo IDENTICAL
IDENTICAL
```

The mirror's output is **byte-identical** to the real repo's. Only then did I measure the patch.

### RUN 3 — the patch, measured

```
$ python3 /tmp/claude-0/w13b/apply_patch.py /tmp/claude-0/w13b/mirror/research/data/emc-clinical-registry.json
patch applied to /tmp/claude-0/w13b/mirror/research/data/emc-clinical-registry.json
$ python3 /tmp/claude-0/w13b/validate_identity_contract.py /tmp/claude-0/w13b/mirror
TOTAL FINDINGS: 34 across 3 files (33 violations, 1 annotated guards)
REAL_EXIT=1
$ diff <(grep '^### ' runB2.txt) <(grep '^### ' runC.txt)
1c1
< ### C1-COUNT-UNIT-UNDECLARED  (14)
---
> ### C1-COUNT-UNIT-UNDECLARED  (9)
5d4
< ### C2-DENOM-UNEXPLAINED  (3)
```

**8 of the 42 findings are cleared: 5 of the 14 C1 violations, and all 3 C2 violations. 34 remain and the validator still exits 1.** The 9 surviving C1s are `cohorts[5..13]`, outside this task's scope. No other check changed. **I did not weaken any check to produce this number** — the validator ran unmodified, extracted verbatim from W13's report.

### RUN 4 — the patch does not damage anything

```
$ node scripts/validate-registry.mjs      # real repo, unpatched
REAL_EXIT=0
$ node scripts/validate-registry.mjs      # mirror, PATCHED
OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).
REAL_EXIT=0
```

Structural diff of unpatched vs patched registry: **18 keys ADDED, 0 CHANGED, 0 REMOVED.** The patch is purely additive; no committed value, key order, or count is altered.

⚠ `scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py` exits **1** — `ModuleNotFoundError: No module named 'pytest'`. This fails identically on the **unpatched** real repo, so it is a pre-existing environment gap, not a consequence of my patch. **I am reporting it as an unrun check, not as a pass.**

### RUN 5 — a live regression caused by the mid-run commit, reported to the coordinator

After `103ff76f` made the campaign reports tracked, the same validator against the same real repo now returns:

```
$ python3 /tmp/claude-0/w13b/validate_identity_contract.py /home/user/Rare-cancers
TOTAL FINDINGS: 50 across 6 files (45 violations, 5 annotated guards)
REAL_EXIT=1
```

**W13's C12 check now fires 4 times on W13's own report** (lines 131, 212, 214, 489 — its prose quoting "12 tumours" and "12 cases"), plus 4 new C12b guards on `W01b`, `W05` and `W13`. These are false positives of exactly the kind W13 documented: a report *describing* a unit-word defect is not *committing* one. If this validator is ever adopted as a gate, it needs a scope exclusion for `research/autonomy/opus-capacity-campaign-20260908/`. **PROPOSED (NOT RUN)** — not my lane to change, and I did not modify the checker.

### PROPOSED (NOT RUN)

- Applying the patch to `research/data/emc-clinical-registry.json`. **Not run, and not mine to run**: the clinical registry is protected state under `systems/POLICY-evidence.md` and this worker is read-only. Routed below.
- Tightening C1 so that a bare `nUnit` key does not satisfy it (see Limitations). A **strengthening**, offered as a proposal; I did not alter the checker I measured against.
- `scripts/preflight.sh`. Not run — the brief forbids it.

## The routed patch

**ROUTED, NOT APPLIED.** Owner: whoever owns `research/data/emc-clinical-registry.json` under `systems/POLICY-evidence.md`. Purely additive: `nUnit` / `nUnitObserved` / `nUnitEvidence` on `cohorts[0..4]`, and `denomNote` inside each of the three Meis-Kindblom outcome objects. The script below is the deterministic form (it preserves committed key order and asserts every value it is keying off, so it fails loudly rather than silently patching the wrong row if the registry has moved).

```python
#!/usr/bin/env python3
"""W13b proposed patch: nUnit on registry.cohorts[0..4]; denomNote on the three
Meis-Kindblom denominators. ROUTED, NOT APPLIED to the repository — this script exists
so the coordinator/registry owner can reproduce the exact edit, and so W13's validator
can be measured against it in a scratch mirror.
Every quoted sentence is from the source's own text, retrieved via PubMed."""
import json, sys, collections
p = sys.argv[1]
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
C = d["registry"]["cohorts"]

def put(obj, key, val, after):
    """Insert key immediately after `after`, preserving committed key order."""
    items = list(obj.items()); obj.clear()
    for k, v in items:
        obj[k] = v
        if k == after:
            obj[key] = val

# --- cohorts[0] ------------------------------------------------------------- PRIMARY
assert C[0]["n"] == 134 and C[0]["sourceId"] == "masunaga2025"
put(C[0], "nUnit", "patient", "n")
put(C[0], "nUnitObserved", True, "nUnit")
put(C[0], "nUnitEvidence",
    "STATED by the source. Masunaga 2025, J Orthop Surg Res, PMC12398172, doi "
    "10.1186/s13018-025-06245-6, Results / 'Patients without metastases at diagnosis': "
    "\"For the prognostic analysis, eight patients who did not undergo surgery were excluded, "
    "and the remaining 134 patients were included.\" The same paragraph states the three "
    "committed event counts in the same unit: \"Local recurrence occurred in 16 patients "
    "(11.9%)\", \"Distant metastases occurred in 39 patients (29.1%)\", \"Nine patients (6.7%) "
    "died due to the tumor\". Retrieved 2026-09-08 via PubMed MCP get_full_text_article.",
    "nUnitObserved")

# --- cohorts[1] ------------------------------------------------------------- PRIMARY
assert C[1]["n"] == 29 and C[1]["sourceId"] == "masunaga2025"
put(C[1], "nUnit", "patient", "n")
put(C[1], "nUnitObserved", True, "nUnit")
put(C[1], "nUnitEvidence",
    "STATED by the source. Masunaga 2025, PMC12398172, Results / 'Patients with metastases at "
    "diagnosis': \"A total of 29 patients had distant metastases at the time of diagnosis.\" "
    "The committed diseaseDeath 9/29 is the sum of the same section's two disjoint sub-groups, "
    "both stated in patients: five of the 16 who received advanced-stage chemotherapy \"died of "
    "the tumors\" and four of the 13 who did not \"died of tumors\". "
    "Retrieved 2026-09-08 via PubMed MCP get_full_text_article.",
    "nUnitObserved")

# --- cohorts[2] -------------------------------------------------------------- UNKNOWN
assert C[2]["n"] == 117 and C[2]["sourceId"] == "meisKindblom1999"
put(C[2], "nUnit", "UNKNOWN", "n")
put(C[2], "nUnitObserved", False, "nUnit")
put(C[2], "nUnitEvidence",
    "UNKNOWN — the source's own word for the 117 is 'cases', not 'patients', and the retrieved "
    "text never equates them. Meis-Kindblom 1999, Am J Surg Pathol 23(6):636-50, PMID 10366145, "
    "doi 10.1097/00000478-199906000-00002, abstract: \"The clinical, morphologic, and "
    "immunohistochemical features of 117 previously unreported cases were studied and "
    "statistically analyzed.\" The abstract attaches patient-level attributes to that same set "
    "(\"The median patient age was 52 years (range, 6-89 years)\"; \"The male-to-female ratio was "
    "2:1\"), which is consistent with one case = one patient but does not state it; a "
    "consultation/referral pathology series can carry two accessioned cases from one patient "
    "(e.g. a primary and its later recurrence). Because this row's own outcome DENOMINATORS are "
    "separately stated in patients (see the denomNote fields), n=117 and the denominators are "
    "not established to be in the same unit. Chiusole 2020 (PMC7308468, Discussion) describes it "
    "SECONDARILY as \"a retrospective series of 117 patients with EMC\", which is a third party's "
    "word, not the source's, and is recorded here as insufficient. NOT RESOLVABLE ON A PERMITTED "
    "ROUTE: the full text is paywalled and is recorded in the campaign CLOSED-WORK inventory as "
    "unrecovered/egress-blocked; no denied route was replayed. Abstract retrieved 2026-09-08 via "
    "PubMed MCP get_article_metadata.",
    "nUnitObserved")

# --- cohorts[3] ------------------------------------------------------------- PRIMARY
assert C[3]["n"] == 60 and C[3]["sourceId"] == "ussc2022"
put(C[3], "nUnit", "patient", "n")
put(C[3], "nUnitObserved", True, "nUnit")
put(C[3], "nUnitEvidence",
    "STATED by the source. Gusho et al. 2022, J Surg Oncol 126(8):1533-42, PMID 35962783, doi "
    "10.1002/jso.27062, abstract Methods: \"EMC patients were identified from the United States "
    "Sarcoma Collaborative database between 2000 and 2016.\" Results: \"Sixty individuals with a "
    "mean age of 55 years were included, and 65.0% (n = 39) were male.\" The committed recurrence "
    "18/60 is verbatim: \"The locoregional recurrence rate was 30.0% (n = 18/60)\". Abstract only "
    "(publisher, not open access); the unit is stated in the abstract, so no full text was needed. "
    "Retrieved 2026-09-08 via PubMed MCP get_article_metadata.",
    "nUnitObserved")

# --- cohorts[4] ------------------------------------------------------------- PRIMARY
assert C[4]["n"] == 49 and C[4]["sourceId"] == "chiusole2020"
put(C[4], "nUnit", "patient", "n")
put(C[4], "nUnitObserved", True, "nUnit")
put(C[4], "nUnitEvidence",
    "STATED by the source. Chiusole et al. 2020, Front Oncol 10:828, PMID 32612944, PMC7308468, "
    "doi 10.3389/fonc.2020.00828, Results / \"Patients' Characteristics\": \"Out of 49 patients "
    "treated with curative intent, 20 patients (40.8%) developed metastases and 14 patients "
    "(28.6%) developed local recurrence.\" This full-text sentence also settles a POLICY-evidence "
    "§2.1(2) question the abstract left open: the abstract gives only percentages (28.6%, 40.8%), "
    "but the full text gives the explicit integers 14 and 20, so the committed event counts are "
    "read, not reconstructed from a percentage. Retrieved 2026-09-08 via PubMed MCP "
    "get_full_text_article.",
    "nUnitObserved")

# --- the three Meis-Kindblom denominators -----------------------------------
MK = C[2]
MK["recurrence"]["denomNote"] = (
    "DENOMINATOR UNIT STATED, GAP UNKNOWN. Source's own sentence (Meis-Kindblom 1999, PMID "
    "10366145, abstract): \"There were local recurrences in 40 (48%) of 83 patients, 23 (58%) of "
    "whom had multiple local recurrences.\" Unit = patient, stated. 40/83 = 48.2%, matching the "
    "source's 48%, so events and denom are read verbatim. WHY 83 and not 117 (or the 99 with "
    "follow-up) is NOT stated anywhere in the retrieved text: missing data, a local-recurrence "
    "assessability sub-stratum, and a differently-defined at-risk set are all consistent with the "
    "abstract and it does not choose between them. UNKNOWN, not inferred. The full text is "
    "paywalled and recorded unrecovered in CLOSED-WORK; no denied route was replayed.")
MK["metastasis"]["denomNote"] = (
    "DENOMINATOR UNIT STATED, GAP UNKNOWN. Source's own sentence: \"Metastases occurred in 35 "
    "(46%) of 76 patients.\" Unit = patient, stated. 35/76 = 46.1%, matching the source's 46%. "
    "The abstract does not say why 76 differs from 83, from the 99 with follow-up, or from 117, "
    "and does not describe 76 as a stratum. UNKNOWN, not inferred. Note that 83 (recurrence) and "
    "76 (metastasis) are NOT stated to be nested or disjoint, so this row contributes a different "
    "population to each pooled outcome. Full text paywalled/unrecovered per CLOSED-WORK.")
MK["diseaseDeath"]["denomNote"] = (
    "DENOMINATOR EXPLAINED: MISSING FOLLOW-UP DATA. Source's own sentence: \"Follow-up "
    "information was available in 99 cases (median, 9 years: range, 2 months-22 years).\" The "
    "117 -> 99 gap is therefore absence of follow-up information, not a different unit and not a "
    "sub-stratum. ⛔ The source's unit word for this denominator is 'cases'; the numerator is "
    "given in patients: \"Forty-eight patients were disease-free, and 41 patients had evidence of "
    "disease (18 of these had died of disease). Ten additional patients survived, but their "
    "disease status was unknown.\" 18/99 is therefore a crude during-follow-up proportion whose "
    "numerator and denominator are stated in different unit words by the source itself. Full text "
    "paywalled/unrecovered per CLOSED-WORK; no denied route replayed.")

json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
open(p, "a").write("\n")
print("patch applied to", p)
```

## The consequence for the pooled headline

**The five pooled `n` values are NOT what the headline sums, and saying so plainly is the most important result here.** `POLICY-evidence.md` §2.2 defines p̂ = (Σ eventsᵢ) / (Σ **denom**ᵢ). The field `n` appears in no pooled arithmetic. So the fact that `cohorts[2].n = 117` has an unresolvable unit **does not corrupt any published number** — it corrupts the row's *label*. W13's framing was right and its corollary is worth stating: the 14 undeclared units are a labelling defect, and for the headline specifically the load-bearing field is `denom`.

**Do the pooled denominators mix units? Almost entirely no — with one seam.** Measured across the `pool: true` set (which is exactly `cohorts[0..4]`):

| pooled outcome | contributing `events/denom` | denominator units, as stated by each source | verdict |
|---|---|---|---|
| recurrence | 16/134, 40/83, 18/60, 14/49 → **88/326 = 27.0%** | patient, patient, patient/individual, patient — all **stated** | ✅ no unit mix |
| metastasis | 39/134, 35/76, 20/49 → **94/259 = 36.3%** | patient, patient, patient — all **stated** | ✅ no unit mix |
| diseaseDeath | 9/134, 9/29, 18/**99** → **36/262 = 13.7%** | patient, patient, **"cases"** | ⚠ **one seam** |

**Quantifying the seam.** The single denominator not stated in patients is Meis-Kindblom's 99, and it contributes **99/262 = 37.8%** of the pooled disease-death denominator. If those 99 cases represent fewer than 99 patients — the failure mode a consultation series makes real — the true patient denominator is smaller and the pooled 13.7% is an **under-estimate**. The direction is determined; the magnitude is **not bounded above by any evidence I hold**, because the full text is unrecoverable. 13.7% is the floor.

**The larger effect is a denominator-*definition* mix, not a unit mix, and it is bigger than the seam.** `cohorts[0]`, `[1]`, `[3]` and `[4]` contribute their **whole stratum** as the denominator (134, 29, 60, 49). `cohorts[2]` contributes an **assessability-restricted subset** to each outcome (83, 76, 99 — all smaller than its own 117), which drops mostly event-free unassessed cases and so pushes each rate up. The size of that effect, computed by re-pooling with Meis-Kindblom's denominator forced to its own n=117:

| pooled outcome | as committed | with MK denom = 117 | shift |
|---|---|---|---|
| recurrence | 88/326 = **26.99%** | 88/360 = 24.44% | **−2.55 pp** |
| metastasis | 94/259 = **36.29%** | 94/300 = 31.33% | **−4.96 pp** |
| diseaseDeath | 36/262 = **13.74%** | 36/280 = 12.86% | **−0.88 pp** |

So **the choice of Meis-Kindblom denominator moves the pooled metastasis headline by ~5 percentage points and the recurrence headline by ~2.5 points**, and until this run nothing in the repository recorded that the choice had been made or on what basis. The committed choice (83/76/99) is the defensible one — it uses the source's own denominators verbatim rather than inventing a larger at-risk set — but it means the pool is averaging "proportion of *all* patients in a stratum" against "proportion of *assessable* patients", which is a heterogeneity the §2.2 range disclosure does not currently name.

⛔ **No clinical claim is made or implied.** Every number above concerns how a proportion is *recorded and combined*, never whether EMC recurrence is 27% or 24%. Adopting this patch changes no scientific conclusion; it makes the existing ones checkable, and it puts a floor and a direction under one of them.

## Limitations

- **`cohorts[2].n` is left UNKNOWN and no amount of further work in this sandbox resolves it.** The Meis-Kindblom full text is paywalled and recorded unrecovered. I did not attempt it, and an abstract that does not state the unit leaves the answer UNKNOWN.
- ⚠ **My own patch exposes a weakness in the check it clears, and I am naming it rather than banking the win.** W13's C1 fires on the *absence of the `nUnit` key*. `cohorts[2]` therefore clears C1 by writing `nUnit: "UNKNOWN"` — by **declaring** its ignorance, not by resolving it. That is the honest record, but it means 5 cleared C1s is not 5 resolved units; it is **4 resolved and 1 documented as unresolvable**. A stronger C1 would require `nUnitObserved: true` **and** a non-empty `nUnitEvidence` before counting a row as resolved, and would report `UNKNOWN` rows in a separate bucket instead of as clean. I included both fields in the patch so that strengthening is possible without another source-reading pass. I did **not** apply it to the validator I measured against, because authoring my own looser-or-tighter acceptance criterion mid-measurement is not permitted.
- **Four rows rest on one retrieval each and two of those are abstracts** (`ussc2022`, `meisKindblom1999`). For USSC the unit is stated *in* the abstract, so no full text was needed; for Meis-Kindblom the abstract is insufficient and that is recorded as UNKNOWN.
- **The 9 remaining C1 violations (`cohorts[5..13]`) are untouched.** Absence of a verdict there is UNKNOWN, not clean. So are all of W13's A3–A12 findings except the two classes I cleared.
- **The "assessability" reading of 83 and 76 is my characterisation of a hypothesis space, not a finding.** The `denomNote` text I propose records the alternatives and explicitly declines to choose.
- The pooled sensitivity table forces MK's denominator to 117 as a **bound-finding device**, not as a proposed correction. Re-pooling on 117 would itself be unsupported, since 117's unit is UNKNOWN.
- `scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py` could not run (no `pytest`). **Unrun, not passed.**

## Stop condition

**Set:** a per-row unit verdict with quoted evidence or an honest UNKNOWN for all five pooled cohorts plus the three Meis-Kindblom denominators; a routed patch; a statement of the consequence for the pooled headline. **Met.**

Four of five cohorts resolved to **patient** with the source's own sentence quoted; one (`cohorts[2]`) recorded **UNKNOWN** with the source's own contradicting word ("cases") quoted and the unrecoverable route named. Of the three denominators: **99 explained** (missing follow-up, quoted), **83 and 76** confirmed **patient-unit** but with the gap **UNKNOWN**, quoted. Patch routed, purely additive, verified to clear **8 of 42** findings (validator exit still 1) and to leave the incumbent gate at exit 0.

## Tool-call and wall-clock count actually used

**21 tool calls; 5 minutes 32 seconds wall clock** (02:06:51Z → 02:12:23Z). Inside the ~40/~40 target.

## Next concrete action

**One successor, finite:** resolve C1 for the remaining nine cohorts (`cohorts[5..13]`) the same way — read each source's own sentence for what its `n` counts. It is bounded by nine `sourceId`s, several of which are already marked `pool: false` for population overlap and so cannot damage the headline, which makes it lower-value than this run and honestly so. The **higher-value** successor is different and belongs to the registry owner rather than a worker: **decide and record whether §2.2's pool may mix whole-stratum denominators with assessability-restricted ones**, given the 2.5–5.0 pp effect measured above. That is a methods decision, not a defect a worker should silently "fix", and it now has a number attached to it for the first time.

---

result: W13b resolved the unit of `n` for all five pooled EMC cohorts from the sources' own sentences via PubMed — `cohorts[0]` (134), `[1]` (29), `[3]` (60) and `[4]` (49) are **stated patients** with quoted evidence, `cohorts[2]` (Meis-Kindblom 117) is **UNKNOWN** because the source's own word is "cases" and its full text is paywalled/unrecovered — and resolved the three Meis-Kindblom denominators (99 = missing follow-up, stated; 83 and 76 = stated in patients but gap UNKNOWN), delivering a purely additive routed patch (18 keys, 0 values changed) that clears 8 of W13's 42 findings in a byte-calibrated scratch mirror (validator still exit 1; incumbent `validate-registry.mjs` exit 0), plus the quantified headline consequence: `n` never enters §2.2's arithmetic, the pooled denominators mix units only at one seam (MK's "cases" 99 = 37.8% of the disease-death denominator, making 13.7% a floor), and the real effect is a denominator-definition mix worth −2.55 pp on recurrence and −4.96 pp on metastasis; nothing was written to the repository.
