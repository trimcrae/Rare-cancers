<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:18:59Z UTC
     agent id a7ba961c91508ea10 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a7ba961c91508ea10.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

- **Worker:** W09g, lane 9 refill, OPUS-CAPACITY-CAMPAIGN-20260908. Successor to W09f, as W09f named.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No `env` variable names a model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the served model from the transcript.
- **Write isolation honoured.** Nothing written under `/home/user/Rare-cancers`; no git write operation; `scripts/preflight.sh` not run; no view hand-edited; no correction applied. All execution under `/tmp/claude-0/w09g/`.
- **HEAD: `98a0833f1ede2cf9cef13790388260567a32e868` at start AND at end — unchanged this run.** `git status --porcelain` identical at start and end (the same eight untracked coordinator-collected report files, none of which this report analyses). ⚠ Not the brief's frozen `92abbcb…`, and past W09f's `a87275c1`. All line numbers are pinned to `98a0833f`.
- **Sources read:** the live checkout only. The frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/` was not needed and not read. **No network at all.**

`date -u` at start: `Tue Sep  8 03:10:20 UTC 2026`. At end: `Tue Sep  8 03:13:37 UTC 2026`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0). The five long proxy lines (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`) are elided as marked; nothing else removed:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
[no_proxy=… elided]
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
[GLOBAL_AGENT_NO_PROXY=… elided]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
[JAVA_TOOL_OPTIONS=… elided]
[NO_PROXY=… elided]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
[npm_config_noproxy=… elided]
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

## Question

**In the three prose field families of `systems/graph/publications.json` that W09f did not systematically cover — `outcome_potential_why`, `working_title`, `posted._evidence` — how many clauses assert a categorical absence about a body of evidence, how many are false or over-scoped against committed counter-evidence, and what is each defective field's measured blast radius in the generated views?**

Open because W09f audited only `what_it_would_claim` and `why_not_written`, named these three families as "a real, named gap", and found two defects in them incidentally without auditing either family.

---

## Prior-work check

Read in full first, as dispatched: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `systems/POLICY-evidence.md`, and `reports/W09b-absence-claim-audit.md`, `W09e-views-blast-radius.md`, `W09f-publications-false-absence-audit.md`.

Commands run and what they showed:

| command | what it showed |
|---|---|
| `python3` key census over `publications.json` | 33 records; `outcome_potential_why` on **33/33**, `working_title` on **7**, `posted` on **1** (`PUB-ASO`) with `_evidence` present → **41 fields**, the exact population W09f left unaudited |
| `grep -rn "nobody followed up\|never followed up\|followed up by anyone" --include=*.json --include=*.md .` | the false clause is **also** in `publications.json:287` (`working_title`) and rendered into **7 view lines**; and it surfaced `emc-sgk1-lane-assessment.md:307`, a *measured* follow-up count for one lead |
| `grep -n "Urbini\|29937513" systems/graph/routes.json` | `routes.json:6584` — W09f's counter-evidence exists verbatim; I re-extracted the passage rather than trusting the quote |
| `sed -n '3690,3696p' systems/graph/routes.json` | `remaining_unknowns[0]` = *"Whether any ligand exists for the EWSR1 half — the second arm's chemistry does not exist."* — the open-question form |
| `grep -n "outcome_potential_why\|working_title\|posted" systems/systems_check.py` | **no hit for `outcome_potential_why` anywhere in the generator** — the finding in R.3 |
| `grep -rn "outcome_potential_why" --include=*.py --include=*.mjs --include=*.js --include=*.sh .` | **zero hits repo-wide**; only the schema, the graph file, `research-ledger.json`, `S37-BRANCH-DEBT.md` and W09f's report mention the name |

Not replayed: W09e's C5 correction (I re-run it only as a **control on my own method**); W09f's ten non-TRUE clauses in `what_it_would_claim`/`why_not_written` (I audit the *other three* families and only cross-reference W09f's findings where a duplicate sits in my scope); PUB-EMC-CLASSIFICATION as a paper (user-closed); the NR4A Perspective refusal; lane 11's source-index; every denied external route. No network was used, so no denied route could be replayed.

---

## Method and inputs

Exactly W09f's method, applied to the three remaining families.

1. Enumerate every field of the three names from the parsed JSON (not by grep).
2. Split each into sentences; hand-classify, because the regex class W09f used over-fires on disclaimers and self-scoped statements.
3. Target class, unchanged from W09b/W09f: *a clause asserting, about a body of evidence (the literature, a corpus, cohorts, "anyone", "the field", "nobody"), that some thing is not recorded, found, reported or studied there.* Disclaimers ("asserts no efficacy") and self-scoped statements ("recorded as UNTESTED") are **not** in the class.
4. Grade each TRUE / FALSE / OVER-SCOPED / UNVERIFIABLE against **committed counter-evidence in this tree**.
5. Blast radius by **whole-field sentinel substitution** on a scratch copy, regeneration with `systems/systems_check.py --write-views`, diff against the committed `systems/views/`, with a **no-edit control first** and a real exit code on every run; the pristine file restored after every sentinel.

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `98a0833f` | tree under test, read-only |
| `systems/graph/publications.json` (33 records) | source under test |
| `systems/schema/publication.schema.json` | `$defs.publication.required` — establishes `outcome_potential_why` is a **required** field |
| `systems/systems_check.py` | the generator actually run; `_pub_title` at `:3157-3167`, table row at `:3219-3226` |
| `systems/views/` (107 top-level entries) | the generated layer, diffed |
| `systems/graph/routes.json:3693` | counter-evidence, PUB-ANDGATE |
| `systems/graph/routes.json:6584` (Urbini 2018 passage) | counter-evidence, PUB-KINASE-LEADS |
| `research/manuscripts/dependency/emc-sgk1-lane-assessment.md:307` | the one lead where "never followed up" **is** measured |
| `/tmp/claude-0/w09g/` | scratch copy; the only place anything executed or changed |

Python 3.11 stdlib only. No network, no paid API, no GPU, no clinical claim.

---

## Result

### R.1 — The population `PRIMARY`

| pass | n |
|---|---|
| records | 33 |
| in-scope fields (`outcome_potential_why` + `working_title` + `posted._evidence`) | **41** (33 + 7 + 1) |
| fields carrying ≥1 **categorical** negative about a body of evidence | **21** |
| such clauses | **22** |
| of those, **non-TRUE** | **6 clauses in 6 fields** |

**Tally: 1 FALSE, 4 OVER-SCOPED, 1 UNVERIFIABLE, 16 TRUE.** The base rate (6/22 defective) is close to W09f's (10/22), which is what you would expect if the two field families share a writer and a failure mode.

### R.2 — The six non-TRUE clauses `PRIMARY`

| # | record · field · `publications.json` line | clause, quoted | verdict |
|---|---|---|---|
| 1 | `PUB-KINASE-LEADS.working_title` · `:287` | *"…that **nobody followed up**"* | ⛔ **FALSE** — R.4. **New; W09f did not find this one.** |
| 2 | `PUB-PARKED-MODALITIES.working_title` · `:436` | *"parked on **a capability that does not exist yet**"* | ⚠ **OVER-SCOPED** — R.5. Confirms W09f's incidental flag. |
| 3 | `PUB-PARKED-MODALITIES.outcome_potential_why` · `:444` | *"Every route parked on **a capability nobody has**."* | ⚠ **OVER-SCOPED** — R.5. **Third copy; W09f named only two.** |
| 4 | `PUB-ANDGATE.outcome_potential_why` · `:16` | *"Names precisely **what does not exist** for the design to be built - a ligand for the EWSR1 half."* | ⚠ **OVER-SCOPED** — R.6. Confirms W09f's flag, **with one correction to how W09f described it.** |
| 5 | `PUB-NEOANTIGEN.outcome_potential_why` · `:409` | *"the paper states that **no proteome-wide novelty search was ever run**"* | ⚠ **OVER-SCOPED** (mild) — R.7 |
| 6 | `PUB-METHODS.outcome_potential_why` · `:342` | *"Valuable - **the field publishes almost none**"* | ❓ **UNVERIFIABLE** — R.8 |

The sixteen TRUE clauses are listed in R.9 with the scope that saves each.

### R.3 — ⭐ The structural finding: `outcome_potential_why` and `posted._evidence` have blast radius **zero**, and `outcome_potential_why` has **no consumer at all** `PRIMARY`

Sentinel substitution measured this, and the generator source explains it:

- `grep -n "outcome_potential_why" systems/systems_check.py` → **no match.** The generator never reads the field. Neither does any other `.py`/`.mjs`/`.js`/`.sh` in the repository (`grep -rn` over all four → zero hits).
- `systems/schema/publication.schema.json` → `$defs.publication.required` **includes `outcome_potential_why`**. So it is a schema-mandatory field on all 33 records that **nothing renders and nothing validates the content of**.
- `posted._evidence` likewise: `PUB_GLYPH` at `:3138` keys off the `state` *string* `"posted"`, not the `posted` object; the object is never rendered. Grepping the views for `qeios-aso-v2-doi-recheck` returns nothing.

⛔ **This inverts the reading a lander would naturally take.** Four of the six defective fields (R.2 #3, #4, #5, #6) are **invisible in every generated view** — a correction to them changes zero view lines and cannot be caught by a view-drift check. They are wrong only in the graph source. The two that are visible are both `working_title`, and they are visible *a lot*.

### R.4 — PUB-KINASE-LEADS.working_title: FALSE, and it is the paper's display name `PRIMARY`

`publications.json:287`: *"Four kinase observations in extraskeletal myxoid chondrosarcoma **that nobody followed up**"*.

This is the same assertion W09f graded **FALSE** at `:286` (*"none has been followed up by anyone"*), against `systems/graph/routes.json:6584`, which I re-extracted verbatim rather than trusting the quotation:

> *"⭐ AND THE SHARPEST EVIDENCE ON THIS ROUTE WAS FOUND 2026-08-27, IN A PAPER THIS ROUTE HAD NEVER READ: PMID 29937513 (Urbini et al., Int J Mol Sci 2018, PMC6073125, DOI 10.3390/ijms19071855) is by the SAME GROUP as the 2014 activation report … and its abstract states, verbatim: 'Recently, we reported on the therapeutic activity of sunitinib in a series of EMC cases, however the molecular target of sunitinib in EMC is unknown.'"*

⚠ **The honest nuance, which I state rather than round off.** Under a strict reading — *"no lead has been taken to a prospective EMC-specific test"* — the Urbini paper does not refute the clause. But *"nobody followed up"* is not that strict statement, and the repository's own record shows the originating group publishing again on the strongest lead. **Read as written, it is false.** Separately, `research/manuscripts/dependency/emc-sgk1-lane-assessment.md:307` shows what the supportable form looks like when it is actually measured, for **one** of the four leads:

> *"published 2006 and never followed up | ✅ **measured: 10 citations in 20 years, none an SGK1 follow-up in EMC**"*

So the repository has an SGK1-specific measurement and no equivalent for the other three; generalising the SGK1 finding to all four is the error.

⛔ **This field is worse than the one W09f fixed, because it is the paper's *name*.** `_pub_title` (`systems_check.py:3157-3167`) returns `working_title` for any record with no `document`, and it is the string used for the L2 cross-link label and the L3 section heading. Measured radius: **6 occurrences across 5 files** (R.10).

**Smallest correct restatement**, entirely from committed content — the record's own `why_not_written` says reading each primary record demoted three of four leads:

> *Four kinase observations in extraskeletal myxoid chondrosarcoma, and what their primary records did to them*

(83 chars; still over the 72-char table clip, so the table row is unaffected either way.) ⚠ **The "unfollowed" framing cannot be rescued by bounding it**, because the counter-evidence is a retrieved follow-up, not an absent search — a bounded-negative rewrite would still be false. If a lander wants the framing, the only defensible version is the *per-lead* one the SGK1 assessment measured, which does not fit a four-lead title.

### R.5 — PUB-PARKED-MODALITIES: W09f's flag confirmed, and a third copy it did not name `PRIMARY`

The over-scoping W09f found at `why_not_written:438` (*"a technology nobody has"*) exists in **three** places, not two:

| field · line | wording |
|---|---|
| `why_not_written` · `:438` | *"parked on a technology nobody has"* — W09f's R.8, already reported |
| `working_title` · `:436` | *"parked on a capability that does not exist yet"* — W09f flagged as out of scope; **confirmed defective** |
| `outcome_potential_why` · `:444` | *"parked on a capability nobody has"* — **not previously named by anyone** |

All three assert a state of the world's technology. The record's own `what_it_would_claim:437` supports only the programme-scoped claim: each park has *"a single named capability … whose arrival would make the route computable"* and a scan trigger.

**Smallest correct restatements:**
- `working_title` → *"Five modalities parked on a capability this programme cannot reach: what would have to land, and how it is being watched for"* (108 chars). ⭐ The corrected clause sits at offset 26–62, still **inside** the 72-char table clip, so the fix is visible in the L3 table row.
- `outcome_potential_why` → *"Every route parked on a capability this programme cannot reach. No result to report."* Radius zero.

### R.6 — PUB-ANDGATE.outcome_potential_why: confirmed OVER-SCOPED, **with a correction to W09f's description of it** `PRIMARY`

⚠ **W09f's dispatch-quoted characterisation is wrong in one respect that matters to a lander.** W09f wrote that this field *"repeats its `what_it_would_claim` clause verbatim"*. It does **not**. Side by side:

| field | text |
|---|---|
| `what_it_would_claim:11` | *"…it names precisely **what does not exist for it to be built, which is** a ligand for the EWSR1 half."* |
| `outcome_potential_why:16` | *"**Names** precisely what does not exist **for the design to be built -** a ligand for the EWSR1 half."* |

Same assertion, **different string**. ⛔ **Consequence: a lander who fixes `what_it_would_claim` and then greps for its exact sentence to find duplicates will not find this copy.** That is exactly the failure mode W09f warned about, one level down.

The over-scoping verdict stands, against `systems/graph/routes.json:3693`, which holds the identical subject as an **open question**: *"Whether any ligand exists for the EWSR1 half — the second arm's chemistry does not exist."* The route layer says UNKNOWN; the publication layer says DOES NOT EXIST.

**Smallest correct restatement:** *"Names precisely what the design lacks — no ligand for the EWSR1 half has been retrieved, and whether any exists is open (`systems/graph/routes.json`, RT-ANDGATE `remaining_unknowns`)."* Radius zero.

### R.7 — PUB-NEOANTIGEN.outcome_potential_why: OVER-SCOPED, mildly `PRIMARY`

`:409` — *"the paper states that no proteome-wide novelty search was ever run."*

W09f graded the source sentence at `:404` **TRUE**, because there it is self-scoped in its own sentence: *"the only novelty test **in this repo** compares against those two PARENT proteins (`fusion_breakpoints.py:231`) and NO proteome-wide search has ever been run"*. The `outcome_potential_why` copy **drops that scope** and keeps only the absolute clause. It retains an attribution (*"the paper states that"*), which softens it — this is the weakest of the four OVER-SCOPED calls, and I grade it as such rather than inflating it.

**Smallest correct restatement:** *"Both routes closed (premise_false, instrument_limit), and the paper states that its only novelty test compares against the two parent proteins, with no proteome-wide search run in this repository."* Radius zero.

### R.8 — PUB-METHODS.outcome_potential_why: UNVERIFIABLE `PRIMARY`

`:342` — *"A failure record. Valuable - **the field publishes almost none** - and by construction not a treatment lead."* This is the same claim W09f found UNVERIFIABLE in the sibling `what_it_would_claim:337`, with the same missing input.

⛔ **No committed evidence supports a positive wording.** **What would settle it:** a denominator — a count of methods papers screened and the fraction of them disclosing failed selectivity claims, recorded with corpus and date in the shape `nr4a3-fusion-targets.json` uses. None is committed, and no network was authorised to build one.

**Honest bounded-negative form, pending that:** *"A failure record. Valuable — this repository has retrieved no comparable disclosure — and by construction not a treatment lead."* That is a statement about a search, not about the field. **I am not manufacturing a positive claim to fill the slot.**

### R.9 — The sixteen TRUE clauses, and the scope that saves each `PRIMARY`

| record · field | clause | why it survives |
|---|---|---|
| `PUB-EMC-CLASSIFICATION.outcome_potential_why` | *"real and, **on a bounded search**, unpublished"* | ⭐ **This is the correctly-scoped form of the clause W09f graded OVER-SCOPED in the same record's `what_it_would_claim` ("MEASURED here for the first time").** The right wording already exists one field away. |
| `PUB-EMC-PROGRAM.outcome_potential_why` | *"owns ZERO routes of its own"* | scoped to the graph; mechanically checkable |
| `PUB-TCIP.outcome_potential_why` | *"NR4A3 appears zero times in either load-bearing artifact"* | scoped to two named artifacts |
| `PUB-MORTALITY-MECHANISM.outcome_potential_why` | *"most **recorded** deaths carry no stated mechanism"*; *"deaths nothing else **on the board** addresses"* | both scoped by their own qualifier (2 clauses) |
| `PUB-STRATEGY-ARCH.outcome_potential_why` | *"listing conditions that never name it"* | scoped to the recruiting trials the paper's own census enumerates |
| `PUB-MONOVALENT.outcome_potential_why` | *"recorded as UNTESTED rather than refuted"* | self-scoped to this repository's record |
| `PUB-IPD-SURVIVAL.outcome_potential_why` | *"the standard admissibility metric does not bound reading error"* | a demonstrated finding; the sibling measurement is W09f's TRUE #17 |
| `PUB-MATRIX-ADDRESS.outcome_potential_why` | *"all three **named** handles came back unfavourable or unreachable"* | scoped to the three handles |
| `PUB-HLA-COVERAGE.outcome_potential_why` | *"an epitope whose presentation is unestablished"* | a status term matching the route's own `premise_false` grade |
| `PUB-DEGRADER.outcome_potential_why` | *"larger than the instruments can resolve"* | instrument limit, scoped |
| `PUB-NR-OUTSIDE-NR4A3.outcome_potential_why` | *"one unread for want of a probe"* | self-scoped to this programme's routes |
| `PUB-ASO.outcome_potential_why` | *"none at a junction any patient **is reported** to carry"* | scoped to reports |
| `PUB-REPURPOSING.outcome_potential_why` | *"bench tests NOT YET RUN"* | self-scoped |
| `PUB-BIOMARKER-DEP.outcome_potential_why` | *"which classes the data rules OUT"* | scoped to the data |
| `PUB-CARE-DELIVERY.working_title` | *"…and what the literature has been looking at instead"* | ⚠ **considered and cleared, borderline.** It is a *relative* claim, and the sibling `what_it_would_claim` states the supportable version: *"the determinants of survival that have been **studied least**"*. It asserts what the literature does look at, not an absence. No committed counter-evidence contradicts it. A stricter reader could grade it OVER-SCOPED; I quote it so that boundary can be redrawn. |

### R.10 — ⛔ `posted._evidence` carries **zero** defective clauses — reported as a plain negative `PRIMARY`

The single largest prose field in the file (2,597 chars) contains **no categorical negative about a body of evidence**. Every statement is a transcribed measurement carrying a run id, an HTTP status and a timestamp (`fetch-literature.yml` runs 33865838566 / 33866439590 / 33870873509). The one negative-shaped statement — *"IT IS REGISTERED IN THE HANDLE SYSTEM RATHER THAN VISIBLE AT CROSSREF"* — is **superseded within the same field two paragraphs later** (*"AND CROSSREF NOW CARRIES IT TOO"*) and retained rather than deleted, which is rule 1.2 applied correctly. The field also states the absent-reading distinction explicitly: *"the pair of 404s alone would have supported 'do not print this identifier', and it was the handle lookup — a different system, asked the same question — that refuted it."*

⭐ **This is the one field family in `publications.json` that is clean, and the reason is visible in it: every sentence names the instrument that produced it.** That is the same property W09b credited for the JSON boolean layer's low defect rate, achieved here in prose.

### R.11 — Measured blast radius `PRIMARY`

Whole-field sentinel, regeneration, diff against the committed views. **Real exit code 0 on every run**, `systems_check: wrote 111 view(s) to systems/views/` on every run (the generator's own count is 111 against 107 top-level committed entries; the control diff below shows the written set is byte-identical to the committed one, so the two numbers are the generator's accounting versus the top-level file count, not a discrepancy I introduced — the same reading W09f recorded).

| record · field | files touched | sentinel occurrences | committed lines removed | exit |
|---|---|---|---|---|
| `PUB-KINASE-LEADS.working_title` ⛔FALSE | **5** — `L2-rt-alk-hit.md:97`, `L2-rt-dnapk.md:96`, `L2-rt-ret.md:95`, `L2-rt-sgk1.md:93`, `L3-publications.md:65` **and** `:427` | **6** | 6 | **0** |
| `PUB-PARKED-MODALITIES.working_title` ⚠ | **6** — `L2-rt-af3-interface.md:82`, `L2-rt-crispr-cas13.md:87`, `L2-rt-glue.md:99`, `L2-rt-ribozyme.md:90`, `L2-rt-riptac.md:103`, `L3-publications.md:71` **and** `:538` | **7** | 7 | **0** |
| `PUB-PARKED-MODALITIES.outcome_potential_why` ⚠ | **0** | **0** | 0 | **0** |
| `PUB-ANDGATE.outcome_potential_why` ⚠ | **0** | **0** | 0 | **0** |
| `PUB-NEOANTIGEN.outcome_potential_why` ⚠ | **0** | **0** | 0 | **0** |
| `PUB-METHODS.outcome_potential_why` ❓ | **0** | **0** | 0 | **0** |
| `PUB-ASO.posted._evidence` (clean) | **0** | **0** | 0 | **0** |
| `PUB-CARE-DELIVERY.working_title` (cleared) | **5** — `L2-rt-metastasectomy.md:84`, `L2-rt-risk-model.md:85`, `L2-rt-surgical-quality.md:85`, `L2-rt-surveillance.md:84`, `L3-publications.md:69` **and** `:501` | **6** | 6 | **0** |
| **control** `PUB-CARE-DELIVERY.why_not_written` | **5** | **6** | **16** | **0** |

⭐ **The control reproduces W09e and W09f exactly** — 5 files, 6 occurrences, **16** committed lines removed (11 prose + 5 blank separators, that field alone containing a literal `\n\n`). My method therefore agrees with the two that produced the findings this task extends.

⭐ **The 72-char title clip decides visibility, and I measured the offsets rather than assuming.** `systems_check.py:3220`: `short = title if len(title) <= 72 else title[:71] + "…"`.

| field | clause offset–end | title len | clause visible in the **L3 table row**? | lines showing the clause in full |
|---|---|---|---|---|
| `PUB-KINASE-LEADS.working_title` | **69–87** | 87 | ⛔ **No** — renders *"…chondrosarcoma that no…"*. Only *"no"* survives. | **5 of 6** (4 L2 link labels + the L3 heading `:427`) |
| `PUB-PARKED-MODALITIES.working_title` | **26–62** | 120 | ✅ **Yes** — inside the clip | **7 of 7** |
| `PUB-CARE-DELIVERY.working_title` | 66–113 | 113 | ⛔ No — only *"what "* survives | 5 of 6 |

⚠ **This partially corrects the dispatch's own premise.** The dispatch expected `working_title`'s radius to differ *because* it renders in the L3 table row. It does render there — but for the FALSE clause the table row is exactly the place the clause is **clipped away**, while the L2 link labels and the L3 heading show it in full. The visibility comes from the L2 cross-links, not the table.

⚠ A lengthening restatement renumbers downstream lines in the affected views; the lander should regenerate and re-diff rather than reuse these line numbers.

### R.12 — The transferable finding `PRIMARY`

W09b located the defect in the summary layer; W09f narrowed it to prose fields with no row to scope them. This run adds the axis that decides *how a lander should triage them*: **within that layer, defect visibility and defect presence are uncorrelated.** The single FALSE clause in my scope sits in the field with the **largest** rendered radius in the file (it is the paper's display name), while four of the five over-scoped/unverifiable clauses sit in a **schema-required field with no consumer whatsoever** — never rendered, never validated, invisible to the view-drift check that is this repository's main defence. A grep-and-fix pass driven by the views would find one of the six.

⛔ **No clinical claim is made anywhere in this report.** No efficacy, safety, selectivity, therapeutic-window or readiness claim is made or implied. There is no wet lab. No patient datum, accession or citation was created; every quotation is from a committed file at `98a0833f`.

---

## Validation evidence

Environment for every run: scratch copy at `/tmp/claude-0/w09g/copy/`, produced by `tar --exclude=./.git -cf - . | tar -xf - -C /tmp/claude-0/w09g/copy` (`TAR_EXIT=0`; `cmp` on `publications.json` → `PUBS_IDENTICAL`). Linux, Python 3.11 stdlib, no network.

### `RUN` — control: regeneration with no edit is a no-op

```
$ mkdir -p /tmp/claude-0/w09g/copy && tar --exclude=./.git -cf - . | tar -xf - -C /tmp/claude-0/w09g/copy
TAR_EXIT=0
PUBS_IDENTICAL
$ ls /tmp/claude-0/w09g/views-committed | wc -l
107
$ cd /tmp/claude-0/w09g/copy && python3 systems/systems_check.py --write-views
systems_check: wrote 111 view(s) to systems/views/
GEN_EXIT=0
$ diff -rq /tmp/claude-0/w09g/views-committed /tmp/claude-0/w09g/copy/systems/views
CONTROL_DIFF_EXIT=0
```

Idempotent at `98a0833f`, so every later diff is attributable to the sentinel alone.

### `RUN` — nine whole-field sentinels (`/tmp/claude-0/w09g/sentinel.py`)

Each iteration restores the pristine file, asserts the JSON-encoded field value occurs **exactly once** in the file (`assert n==1`, which held for all nine), substitutes `ZZQQSENTINELZZQQ`, regenerates, walks every view file including the `registers/` subdirectory, counts sentinel occurrences and unified-diff `+`/`-` lines against the committed set, then restores and regenerates. `SCRIPT_EXIT=0`. Verbatim output, transcribed into R.11:

```
== PUB-ANDGATE.outcome_potential_why  len=93 GEN_EXIT=0 stdout="systems_check: wrote 111 view(s) to systems/views/" sentinel_occurrences=0 files_changed=0 committed_lines_removed=0 lines_added=0
== PUB-KINASE-LEADS.working_title  len=87 GEN_EXIT=0 ... sentinel_occurrences=6 files_changed=5 committed_lines_removed=6 lines_added=6
     L2-rt-alk-hit.md  @@ -97 +97 @@   sentinel_hits=1
     L2-rt-dnapk.md  @@ -96 +96 @@     sentinel_hits=1
     L2-rt-ret.md  @@ -95 +95 @@       sentinel_hits=1
     L2-rt-sgk1.md  @@ -93 +93 @@      sentinel_hits=1
     L3-publications.md  @@ -65 +65 @@ @@ -427 +427 @@   sentinel_hits=2
== PUB-PARKED-MODALITIES.working_title  len=120 GEN_EXIT=0 ... sentinel_occurrences=7 files_changed=6 committed_lines_removed=7 lines_added=7
== PUB-PARKED-MODALITIES.outcome_potential_why  len=67 GEN_EXIT=0 ... sentinel_occurrences=0 files_changed=0
== PUB-METHODS.outcome_potential_why  len=104 GEN_EXIT=0 ... sentinel_occurrences=0 files_changed=0
== PUB-NEOANTIGEN.outcome_potential_why  len=125 GEN_EXIT=0 ... sentinel_occurrences=0 files_changed=0
== PUB-CARE-DELIVERY.working_title  len=113 GEN_EXIT=0 ... sentinel_occurrences=6 files_changed=5 committed_lines_removed=6 lines_added=6
== PUB-CARE-DELIVERY.why_not_written  len=1762 GEN_EXIT=0 ... sentinel_occurrences=6 files_changed=5 committed_lines_removed=16 lines_added=6
== PUB-ASO.posted._evidence  len=2597 GEN_EXIT=0 ... sentinel_occurrences=0 files_changed=0
RESTORE_GEN_EXIT=0 "systems_check: wrote 111 view(s) to systems/views/"
SCRIPT_EXIT=0
```

### `RUN` — zero-radius corroborated independently of the sentinel

```
$ grep -n "outcome_potential_why" systems/systems_check.py          -> no match
$ grep -rn "outcome_potential_why" --include=*.py --include=*.mjs --include=*.js --include=*.sh .   -> no match
$ grep -rn "Names precisely what does not exist for the design" systems/views/   -> no output
$ grep -rn "A failure record. Valuable" systems/views/                          -> no output
$ grep -rn "qeios-aso-v2-doi-recheck" systems/views/                            -> no output
```

and `systems/schema/publication.schema.json` → `$defs.publication.required` = `["id","level","kind","state","target_venue","what_it_would_claim","outcome_potential","patient_path","outcome_potential_why","unit"]`.

### `RUN` — clip-offset measurement

```
PUB-KINASE-LEADS:      len=87  clause_offset=69  clause_end=87
PUB-PARKED-MODALITIES: len=120 clause_offset=26  clause_end=62
PUB-CARE-DELIVERY:     len=113 clause_offset=66  clause_end=113
```
against `systems_check.py:3220` `short = title if len(title) <= 72 else title[:71] + "…"`, and the rendered rows at `L3-publications.md:65,69,71` inspected directly, confirming the `…` truncation.

### `RUN` — isolation proof

```
$ git rev-parse HEAD   (start) -> 98a0833f1ede2cf9cef13790388260567a32e868
$ git rev-parse HEAD   (end)   -> 98a0833f1ede2cf9cef13790388260567a32e868
$ git status --porcelain (start == end) -> the same 8 untracked coordinator report files, nothing else
$ cmp .../copy/systems/graph/publications.json /home/user/Rare-cancers/systems/graph/publications.json
SCRATCH_PUBS_RESTORED_IDENTICAL
$ diff -rq /tmp/claude-0/w09g/views-committed /tmp/claude-0/w09g/copy/systems/views ; FINAL_VIEWS_DIFF_EXIT=0
$ diff -rq /home/user/Rare-cancers /tmp/claude-0/w09g/copy --exclude=.git ; TREE_DIFF_EXIT=0
```

⭐ HEAD did **not** move this run, so nothing I measured changed under me; and the final tree diff is empty, so the scratch copy is byte-identical to the live tree, in `systems/graph/`, `systems/views/` and everywhere else.

### `PROPOSED (NOT RUN)`

- **Correction diffs for the six defective fields.** Only the *sentinel* radius was measured; the restatements were not applied and not re-diffed. The clip-visibility conclusions in R.11 are derived from **measured offsets**, not from an applied edit.
- **Acceptance tests.** Shape only, per W09f's warning: any test must assert the superseded sentence is **quoted-and-superseded** inside `⚠ Superseded, retained (rule 1.2): "…"`, never **absent** — a bare grep fires on the retained quotation. For `PUB-KINASE-LEADS.working_title` there is an added trap: the same false string also lives at `:286`, which is W09f's fix, not mine, so a repository-wide grep-for-absence would couple the two landings. Not written, not run.
- **A methods-paper denominator** for R.8 — would require retrieval; no network authorised.
- **Independent retrieval of PMID 29937513 or the SGK1 citation count** — no network authorised; both quotations are from committed files.
- `scripts/preflight.sh` — forbidden by dispatch, and no edit exists to gate.
- **The same audit over `routes.json`, `strategies.json`, `modalities.json`, `objects.json`** — W09f's second-half suggestion; out of this dispatch's scope and not started.
- Landing anything. Nothing was applied to the repository.

---

## Limitations

- **FALSE / OVER-SCOPED here means "a committed counter-record exists in this tree", not "I searched the literature."** A clause I graded TRUE could still be false against sources this repository has never retrieved. No network was used.
- **R.4's FALSE verdict is reading-dependent, and I have said so rather than hiding it.** *"nobody followed up"* is refuted by a retrieved follow-up; the stricter statement it may have been reaching for (*no prospective EMC-specific test*) is neither refuted nor verified by anything committed.
- **The 22-clause count depends on my class boundary**, which is W09f's and W09b's. A reader who counts disclaimers gets a much larger number; one who demands an explicit `nobody`/`never`/`no ... exists` token gets about 8. Every clause is quoted so the boundary can be redrawn without re-running anything.
- **`PUB-CARE-DELIVERY.working_title` is a judgement call graded TRUE**, and a stricter reader could grade it OVER-SCOPED. Its sentinel radius is measured either way.
- **Zero radius is measured at this HEAD and this generator.** If a future renderer starts consuming `outcome_potential_why`, four currently-invisible defects become visible; the finding is about the generator as committed, not a permanent property.
- **Line numbers are at `98a0833f`**, and view line numbers shift once any length-changing correction is regenerated.
- **No clinical, efficacy, safety, selectivity or readiness claim** is made or implied. `systems/POLICY-evidence.md` binds the clinical registry and pooled proportions derived from published cohorts; `systems/graph/publications.json` is outside its scope, and nothing proposed here touches a registry datum, a pooled proportion or an interval.
- **Nothing was landed**, no view was hand-edited, no test was authored or relaxed, no guard changed.

---

## Stop condition

Set up front: *return the moment all 41 `outcome_potential_why` / `working_title` / `posted._evidence` fields are enumerated and classified, every non-TRUE field has a regeneration-measured blast radius with a real exit code, every one has a smallest correct restatement or a stated settling condition, W09f's two incidental findings are confirmed or corrected, and the pristine file is verified restored.*

**MET.** 41 fields enumerated, 22 categorical clauses classified (1 FALSE / 4 OVER-SCOPED / 1 UNVERIFIABLE / 16 TRUE), 9 sentinels measured at `GEN_EXIT=0` with the C5 control reproducing W09e and W09f exactly, a restatement or settling condition for all six non-TRUE clauses, W09f's PARKED-MODALITIES flag confirmed and its ANDGATE "verbatim" description corrected, and `TREE_DIFF_EXIT=0` proving restoration.

---

## Tool-call and wall-clock count actually used

**23 tool calls. 3 minutes 17 seconds wall clock** (03:10:20Z → 03:13:37Z), plus report drafting. Well inside the ~40-call / ~40-minute target; I stopped when the condition was met rather than padding.

---

## Next concrete action

**Land the `PUB-KINASE-LEADS.working_title` correction alone, together with W09f's `:286` correction, as one atomic change — and land nothing else from either report in the same commit.** Concrete, bounded, and the only item where a defect is both **FALSE** and **rendered into 6 view lines across 5 files** including the paper's display name in 4 L2 cross-links. The two must move together because the identical false string sits at `:286` and `:287`, so fixing one leaves the other visible one line away and makes any absence-shaped acceptance test ambiguous. Radius is measured (R.11), the counter-evidence is quoted verbatim from `routes.json:6584`, the restatement is given in R.4, and the lander must regenerate and re-diff rather than reuse these line numbers.

Second, separately and lower priority: the four zero-radius `outcome_potential_why` defects (R.5 #3, R.6, R.7, R.8) are source-only and invisible to the view-drift check — they need a **schema or validator** decision first, because R.3 shows the field is schema-required with no consumer at all, and "correct the prose in a field nothing reads" may be the wrong repair compared with giving the field a checker.
