<!-- collected 2026-09-08T03:43:42Z by campaign coordinator; agent id a5dbde5d31a00822a; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a5dbde5d31a00822a.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report below.

---

## Worker

**W36**, successor routing index (routed-but-unlanded surface across the whole report corpus), OPUS-CAPACITY-CAMPAIGN-20260908. Advisory index only — I performed no repair, adjudicated no ruling, decided no owner's question.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. I did not observe the served model. No environment variable in this container names a model; the coordinator must extract the actual per-child runtime model from the transcript.

Literal `env | grep -i -E 'model|claude'` output at start (secrets redacted by the grep's own pattern set; nothing matching TOKEN/KEY/SECRET appeared in this narrower grep):

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
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
```

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:31:46 UTC 2026` | `Tue Sep  8 03:36:25 UTC 2026` |
| `git rev-parse HEAD` | `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1` | `1c9d827870599576c0c027a9134363d59456fd04` |
| `git status --porcelain` | empty (0 lines) | empty (0 lines) |
| `ls reports \| wc -l` | **150** | **157** |

⚠ **HEAD moved under me.** `215ed8e7` → `793f63cb` (collect W01i, W33, W06h, W09h, W03f, W14e, W29b, W35) → `1c9d8278` (campaign briefs corrected). **This index is pinned to the 150 reports present at `215ed8e7`.** The seven added mid-run — `W01i`, `W33`, `W06h`, `W09h`, `W03f`, `W29b`, `W35` — are **not indexed at all, and their contents are UNKNOWN to me.** (`W14e` was already present at `215ed8e7` and is indexed.) `git diff --name-only 215ed8e7 HEAD` outside the campaign directory returns nothing, so every `file:line` anchor below is still valid at the end HEAD.

**Zero files created or modified under `/home/user/Rare-cancers`. No git write. No network, no MCP, no paid API, no GPU.** Scratch was `/tmp/claude-0/w36/`; I needed no files in it and **deleted it** (`rm -rf` verified: `ls: cannot access '/tmp/claude-0/w36'`).

**W25 is HELD/EXCLUDED**, per the safety receipt in `SAFETY-EVENTS.md`: the writer's W25-associated continuation is HELD after two turns blocked by safety systems with **scope UNKNOWN**. I read nothing from `reports/W25-gse243553-candidate-merit.md`, extracted nothing from it, and route nothing out of it. Where another report cites W25 (e.g. `W23b:264` cites "already routed by W25:178"), I record the citing report's words and do not open W25.

---

## Question

**What is the complete routed-but-unlanded surface of this campaign — every proposed change, priced wiring, identified-but-refused ruling and named measurement request that a report handed to an owner and did not land — indexed with report and line, target file, owner, blocker, conflicts and class; and is that surface growing faster than it is being resolved?**

Open because W24, the nearest prior art, indexed 27 of 92 reports and states at its own Limitations that it did not read the other 65 and that their absence is UNKNOWN. The corpus is now 150 files (157 by the time I finished). Nobody can see the surface whole, and no report has ever asked the growth-versus-resolution question.

---

## Prior-work check

Read **in full**: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `SAFETY-EVENTS.md`, and `reports/W24-repair-routing-index.md` (310 lines, read end to end across four `sed -n` ranges).

Commands and what they showed:

- `ls | sed 's/-.*//' | sort | uniq -c` → **150 reports**, lanes W01–W31 with suffixes. W24 saw 92→99.
- Marker-density census over all 149 (W25 skipped): `grep -c -i -E "routed|not applied|owner'?s call|owner must|owner decides|PROPOSED \(NOT RUN\)|did not apply|coordinator decision|belongs to (its|the) owner|owner'?s (judgement|decision)|left to the owner"` per file → the ranked list that drove every targeted extraction. W24 (33) is the top hit; the corpus below it has 78 files with ≥2 hits.
- Path × routing co-occurrence: `grep -n -E "(research|scripts|systems)/[A-Za-z0-9_./-]+\.(py|json|md|sh|mjs|tsv)" | grep -i -E "<routing markers>"` across all 149 → the target-file column, with report and line, straight out of the reports.
- `awk '/^#+ .*[Nn]ext concrete action/{p=1;next} p&&/^#+ /{exit} p'` over ~100 reports → the residual each report handed on.
- Tree verification (see Validation evidence): existence and unlanded-status checks on 25 target paths.

**Closed items I confirm I am not replaying, reopening or relabelling:** the NR4A Perspective content-policy refusal (not recreated, not rerouted, not relabelled, not indexed as an open route); the user-rejected registry ICD-O paper; methylation; the clinical conditional-recurrence / RT-IPD / trial-discoverability checkpoints; paired Davis; promoter transfer; Brenca case identity; Hofvander/EGA; GSE4303/GSE28866 re-reads; every denied retrieval route in `CLOSED-WORK.md`. **I made zero network calls.** W25 is untouched.

**I am succeeding W24, not duplicating it.** W24's rows R01–R26, D01–D20 are carried forward by reference with their W24 identifiers where they still stand; everything with a `U`-number below that W24 did not have is new. Where I contradict W24 I say so and show the command.

---

## Method and inputs

- Live cloud checkout `/home/user/Rare-cancers` at `215ed8e7` (read set) → `1c9d8278` (end). I did **not** read the frozen corpus at `/tmp/claude-0/frozen-corpus/`; every corpus-dependent statement below is transcribed from W21/W21b/W21c/W21d/W23b and marked SECONDARY.
- Tools: `git` (read-only), `grep`, `sed`, `awk`, `ls`, `wc`, `python3` 3.11 stdlib (`json`). Nothing else.
- **Counting rule for an "item":** one distinct (proposed change **or** identified-and-refused decision **or** named measurement request) × (one target). Two reports proposing the same change to the same target are one item with two anchors. Two reports proposing *different* changes to one target are two items plus a conflict pair.

---

## Result

### Legend

**Class**: `DEF` = defect (something in the tree is wrong or a guard is missing) · `DIS` = disclosure gap (a claim is over-stated, unhedged, or renders wrong text to a reader) · `DEC` = decision explicitly identified and refused · `MEA` = measurement or retrieval request.
**Verified**: `V` = I checked the target in the tree this session and the change is genuinely **unlanded** · `T` = transcribed from the report only, not checked · `V*` = checked and I found something that **contradicts** the report.

---

### Tier 1 — targets transcribed into `systems/graph/` or an active manuscript (highest reach: a wrong or unmade change here propagates to generated views or to a reader of a paper)

| # | Report:line | What it is | Target | Owner as stated | Blocked on | Conflicts with | Class | Ver |
|---|---|---|---|---|---|---|---|---|
| U01 | `W09c:265-300` (=W24 R14) | Replacement note text for `ART-RT-CONTRADICTION` + `ART-CARE-DELIVERY-EVIDENCE`, with RED/GREEN acceptance test | `systems/graph/artifacts.json` | graph owner / coordinator (S18 queued row) | nothing | — | DEF | T |
| U02 | `W09e` Result/Stop | Full correction diff for the C5 clause of `PUB-CARE-DELIVERY.why_not_written` | `systems/graph/publications.json:119` | graph owner | nothing | **U02a** | DEF | T |
| U02a | `W09d:203,330` | Says the same C5 package is **"Not written, not applied"** and "needs the C3/C4 narrowing decision, which is not mine" | same | same | the C3/C4 narrowing decision | **U02** — a status disagreement: one report supplies wording, the other says nobody has packaged it | DEC | T |
| U03 | `W09g` next action | Land `PUB-KINASE-LEADS.working_title` correction **together with** W09f's `:286` correction as one atomic change | `systems/graph/publications.json` | graph owner | nothing | — | DEF+DIS | T |
| U04 | `W09g` second | Four zero-radius `outcome_potential_why` defects; source-only, invisible to view-drift check | `systems/graph/publications.json` | schema/validator owner | a schema decision first (field is schema-required with no consumer) | — | DEC | T |
| U05 | `W09f` next action | Audit `outcome_potential_why`/`working_title`/`posted._evidence`, then the same names across `routes.json`, `strategies.json`, `modalities.json`, `objects.json` | `systems/graph/*.json` | unassigned | nothing | — | MEA | T |
| U06 | `W26` next action | Land the **six FALSE clauses only** — a 6-field, 11-line change touching `routes.json:6399,:6505,:6607,:6712` (+2) and 6 view files | `systems/graph/routes.json` | unassigned ("the lander") | nothing | — | DEF | V (`:6399`/`:6505` verified byte-identical clause present) |
| U07 | `W26` next action | The **twelve OVER-SCOPED clauses** deliberately left for a separate decision | same | unassigned | a scoping decision | — | DEC | T |
| U08 | `W05:220`, `W05b:192` | Narrow "three independent EMC cohorts" / "three independent measurements" to name *platform* independence | `systems/graph/routes.json` + `nr4a3-fusion-transcriptional-output` manuscript | coordinator; "these files are not mine" | nothing | — | DIS | T (note: the manuscript path W05b names does **not** exist as written; the tree has `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-*`) |
| U09 | `W19b:437-463`, next action | Apply caveat **A** at six named locations, fold residue **B** into `RT-ASYMMETRIC`, regenerate `systems/views/` | `systems/graph/` + views | degrader-selectivity owner | nothing | — | DIS | T |
| U10 | `W19b:451` | Notification only: PMID 41315062 filed under NR4A3 "Variant 5′ partners" is a **different 3′ gene** | `aso-citations-priorart-2026-08-08.md:140`, `fusion-junction-aso-working-record.md:1782` | **PUB-ASO owner** | PUB-ASO is excluded from standing grants | — | DIS | T |
| U11 | `W31:308` | Add a `[G3]` finding listing `systems/views/**/*.md` on disk, erroring on orphans — ~4 lines beside the existing loop | `systems/systems_check.py:4535` | this lane / gate owner | nothing | — | DEF | V (`def check_views` at `:4535` confirmed; no `G3` present) |
| U12 | `W31` secondary | The 152-error clean-tree baseline of `systems_check --check` makes preflight's systems step unattributable | `systems/systems_check.py` / `scripts/preflight.sh` | **"whoever owns the gate"** — unassigned | nothing | — | DEF | T |
| U13 | `W17g:249-262` (=W24 R18) | `0.41× that standard error` at line 761 is wrong; two defensible forms given (`0.37×` at n=565, or `0.37–0.38×`) — a routing note, not a patch | `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md:761` | **PUB-ATR manuscript owner** | the choice between the two forms | must precede U14 and U16 | DIS+DEC | **V** — `sed -n '761p'` still reads `clears it by **0.0155, 0.41× that standard error**` |
| U14 | `W17c:155-175` (=W24 R19) | ~14-word insertion naming the t critical values on the Welch df | same manuscript `:566-567` | PUB-ATR owner | nothing | ordering with U13 | DIS | T |
| U15 | `W17e:R5`, `W17g:~240` (=W24 R16/R17) | 11 candidate `artifact_figures` entries + 1 further entry with `"scale": -1.0` | `research/manuscripts/pinned-figures.json` | PUB-ATR / pin-registry owner | U13 must land first or with it | complementary with U16 | DEF | V (file has 99 `artifact_figures`; the ATR entries are not among them by grep) |
| U16 | `W16d:187-189` | **Five more** `artifact_figures` entries, 0 findings against the live tree, 5 findings in each of two opposite negative controls | same file | PUB-ASO / manuscript owner | nothing | same target as U15 — **three reports now propose additions to one pin file** | DEF | T |
| U17 | `W28:316` | Decide whether `fusion-junction-neoantigen-paper.md` belongs in `targets[]`, then re-run `lint_consistency.py` and adjudicate | `research/manuscripts/pinned-figures.json` `targets[]` | **owner of `pinned-figures.json`** | a decision | — | DEC | **V** — `grep -c 'fusion-junction-neoantigen-paper'` → **0** |
| U18 | `W17e:188,404` (=W24 R21/D15) | `_dig_json` bracket/escape support, **or** a flat mirror field in the artifact | `research/manuscripts/lint_consistency.py` | tooling **and** manuscript owner (two owners must agree) | the two owners agreeing | — | DEC | T |

### Tier 2 — protected shared state and the commit gate

| # | Report:line | What it is | Target | Owner | Blocked on | Conflicts | Class | Ver |
|---|---|---|---|---|---|---|---|---|
| U19 | `W13b:239-275`, `:241` (=W24 R01) | Deterministic additive patch: `nUnit`/`nUnitObserved`/`nUnitEvidence` on `cohorts[0..4]` + `denomNote` ×3. **"ROUTED, NOT APPLIED."** | `research/data/emc-clinical-registry.json` | registry owner under `systems/POLICY-evidence.md` | registry-owner authority | complementary with U20 (apply U19 first) | DEF | **V** — `grep -c '"nUnit"'` → **0**; `grep -c denomNote` → **0** |
| U20 | `W13c:318-348`, `:322` (=W24 R02) | Same shape for `cohorts[5..13]`; explicitly **extends** U19 | same | same | same | ordered after U19, not conflicting | DEF | **V** (same greps) |
| U21 | `W05d:180` (=W24 R24) | Smallest correct repair is an **addition, not a relaxation**: a `periodBasis` field on the registry schema | registry schema | **"W05's owner"** | a schema decision | — | DEC | **V** — `grep -c periodBasis` → **0** |
| U22 | `W13` post-A12 note (=W24 D06) | A validator-enforced `evidenceQuestions[]` rule at `validate-registry.mjs:124` whose subject W13/W24 report as absent | `research/data/emc-clinical-registry.json` | registry owner | "UNKNOWN as to intent" | — | DEC | **V\*** — **CONTRADICTED at HEAD.** `evidenceQuestions` is present at `:1707` and is a top-level key. Full top-level key list at HEAD is `schemaVersion, meta, overview, studies, outcomes, registry, treatments, emergingTreatments, clinicalTrials, monitoring, supportGroups, centers, questionsForOncologist, evidenceQuestions` — **not** the seven-key list W24 D06 quotes. I do not adjudicate whether the rule is satisfied; I record that the premise "no `evidenceQuestions` at all" is false at `215ed8e7`. |
| U23 | `W30` next action, `:323` | Correct whichever of two registry fields `PMC4946242` contradicts (F1), and set that citation's `verified` flag to what was actually checked | `research/data/emc-clinical-registry.json` | **coordinator edit** | **one retrieval — which W07f has already proven reachable at $0.** W30 declined it on scope, not on access | — | DEF | T |
| U24 | `W30` subordinate | F2's four half-repointed secondary rows; repointing `cohorts[8]` from `remiszewski2025` to `stacchiotti2019pazopanib` | same | unassigned ("a separate, larger decision") | re-reading the phase-2 primary — **CLOSED-WORK denial territory** | — | DEC | T |
| U25 | `W16c:204`, `W16b` next action, `W13e:219` (=W24 D12) | The `bishop2019` clause. **The cost nobody had costed: R1/R2/R2b all require editing a registry that is byte-pinned inside a DOI-minted deposit.** | registry + admissibility rule | admissibility-rule owner | a rule decision, and the DOI re-stamp judgement (=W24 D11) | shares a blocker with U19–U24 | DEC | T |
| U26 | `W12d:217-268` vs `W12c:319-341` vs `W12b:150-330` (=W24 R11/R12/D02) | One env line in the gate: `PYTHONUTF8=1` (W12d, 18/18 rc=0) vs `PYTHONIOENCODING=utf-8` (W12c) vs a five-module source form (W12b) | `scripts/preflight.sh` | **preflight owner** — W12c: "Owner's call; I am not making it." | only the choice | **3-way conflict, 3 pairs** | DEF+DEC | **V** — `grep -c PYTHONUTF8` → **0**; `grep -c PYTHONIOENCODING` → **0** |
| U27 | `W12e:325`, `W12f` next action | The lane's own closure: hand W12b→W12e to the preflight owner as **one one-line change with the evidence chain attached**; both close named UNKNOWNs (147 kwargs, 115 sites / 114 INHERITS / 0 REPLACES) | same | preflight owner | the U26 decision | — | DEC | T |
| U28 | `W13g:262` | Add `emc_rt_bed_reappraisal.py\|RT BED reappraisal\|--check` as a **19th row**. "one line and no budget argument required" | `scripts/preflight.sh:847-864` | preflight owner | nothing | with U31, U32 | DEF | **V** — `grep -c emc_rt_bed_reappraisal scripts/preflight.sh` → **0** |
| U29 | `W13g` second | A **20th row** for `emc_relative_survival.py` — but its generator has no `argparse`, so the `--check` must be **written first** | same + `research/manuscripts/emc_relative_survival.py` | preflight owner + generator owner | generator-authoring effort | sequenced after U28 | DEF | **V** — `grep -c argparse emc_relative_survival.py` → **0**; `grep -c emc_relative_survival scripts/preflight.sh` → **0** |
| U30 | `W13g:234` | One-word change: `warns.push` → `errors.push` at `validate-registry.mjs:88` for `pool:false` without `contextReason` | `scripts/validate-registry.mjs:88` | registry/policy owner | ⚠ **"would this turn the tree red today? Unknown"** — by the report's own words | — | DEC | T |
| U31 | `W14e:392` | Wire the **nine `GUARDED-NOT-ENFORCED` rows — and only those nine** — into the gate array | `scripts/preflight.sh` | unassigned | nothing | **conflicts with U39** | DEF | T |
| U32 | `W14:215,368` (=W24 R04-R06 residual) | Add the three fixed generators as gate rows. `PROPOSED (NOT RUN)`: "The three fixed scripts are now *eligible* for it; I did not make them members." | `scripts/preflight.sh` | unassigned | the repairs U34–U36 must land first | — | DEF | T |
| U33 | `W09b:265` | Wire `lint_absence_claims.py --warn-as-error` into preflight — **"Not run, and not recommended at A1/A2's current precision. A3-only would be safe today."** | `scripts/preflight.sh` | unassigned | precision of A1/A2 | — | DEC | T |
| U34 | `W29` next action | Give the gate a per-row "what did this row actually examine?" count for rows 16, 17, 18 (five vacuous paths) | `scripts/preflight.sh` | unassigned | nothing | — | MEA+DEF | T |
| U35 | `W03e:238,391` | One-string wiring: `python3 $MOD/aso_noncoding_acceptor_screened_table.py --check` into `regenerate_aso_chain.sh:265` — the one real generator guard the chain never calls | `regenerate_aso_chain.sh:265` | PUB-ASO / chain owner | should land **with** U36's decision | — | DEF | T |
| U36 | `W03e:391`, R3 | The `submission_citations.py` repair — ready and proven to discriminate, but it edits a generator **inside the PUB-ASO package** | `submission_citations.py` | **PUB-ASO paper owner** | PUB-ASO ownership (excluded from standing grants) | bundled with U35 | DEF | T |

### Tier 3 — generators, artifacts and tests (reach: whatever consumes the artifact)

| # | Report:line | What it is | Target | Owner | Blocked on | Conflicts | Class | Ver |
|---|---|---|---|---|---|---|---|---|
| U37 | `W14c:266-360` (R07) **vs** `W14d:115-232` (R08) | Two whole, independently proven, mutually exclusive repairs to one `--check` | `research/modalities/emc_fourth_cohort_quant.py` | coordinator/tooling (=W24 D01) | the choice only | ⛔ **either/or, 1 pair** | DEF+DEC | T |
| U38 | `W24b:243`, `W24c` | Narrows U37: **C3 conflicts textually with R07's hunk and not with R08's**; W24c ran D3 against R07 and its named next action is to *correct W24's own index row* | same | coordinator | — | second conflict pair on this file (C3 × R07) | DEF | T |
| U39 | `W20h` second, `W20g` second | Add `probe_counts_sha256` to the `--check` drift-key tuple. "One line, no scientific content." | `emc_fourth_cohort_quant.py:940-941` | "the module's owner" | nothing | is the C3 of U38 | DEF | **V** — `probe_counts_sha256` is written at `:819` but the tuple at `:941` carries only `gene_counts_sha256` |
| U40 | `W20e:260`, `W20f` next action | Repair the `n_probes_common_to_every_read_run` intersection filter at `:583`; costed at 44.3 MB, non-destructive | same file `:583` | unassigned | **the k=2 gene-recovery count needs an Actions runner** | fourth routed change to one file | DEF | T |
| U41 | `W06d:133-180` (=W24 R03) | `IMPOSSIBLE_FRACTION_QUOTABLE_MAX` + `quotability()` readout | `research/manuscripts/emc_mortality_decomposition.py` | generator owner | `pytest` absent in W06d's environment — "The generator's owner must run it" | 3-way sequencing with U42, U43 | DEF | **V** — `grep -c quotability` → **0** |
| U42 | `W14:144-232` (=W24 R04) | A `--check` guard for the same file (before: `9 failed`; after: `9 passed`) | same | generator owner | nothing | sequencing with U41, U43 | DEF | T |
| U43 | `W06f:186`, `:321,331` | `smallest_coherent_share_pct` field — **"the patch (returned inline, NOT APPLIED)"**; extends U41 because W06e showed pairing units understate the margin (0 pairings vs 1.30 pp) | same | generator owner | `pytest`; read-only constraint | **third report on one file — W24 saw only two** | DEF | **V** — `grep -c smallest_coherent_share_pct` → **0** |
| U44 | `W06e:266` | Names the shape of U43 as the fix; itself routes nothing further | same | — | — | — | DEC | T |
| U45 | `W14:130-232` (=W24 R05/R06) | `--check` guards for two more generators, same before/after suite | `emc_relative_survival.py`, `emc_terminal_events.py` | generator owner | nothing | U29 depends on the first | DEF | T |
| U46 | `W06b:211-230`, `:91` | One `design_tier` field at line 599, exact replacement string given, **"I did not edit the file"** | `research/manuscripts/emc_systemic_therapy_pooling.py:599` | generator owner | nothing | same file as U47 | DIS | T |
| U47 | `W05f:160-162` | "Smallest correct restatement, **ROUTED AND NOT APPLIED**", marked `PREDICTION` because acceptance is not the author's to grant | same file | **W05 (rubric owner) + generator owner** | nothing | same file as U46, different line | DIS | T |
| U48 | `W05e:255,342` (=W24 R23) | Two items: the `why_excluded` window-arithmetic clause, and the `pool_reason` half-truth (IMMUNOSARC I's EMC subset **is** partly separately reported: n=4, 1 PR) | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` | unassigned | nothing | — | DIS | T |
| U49 | `W06b:230` (=W24 D20) | `emc-mortality-decomposition-inputs.json` carries no design/confirmation field at all — reported, **fix deliberately not proposed** ("a design change… needs its owner's judgement") | that file | unassigned | a design judgement | — | DEC | T |
| U50 | `W16e` next action | Extract the artifact dict from `main()` into a top-level `build()`, add exactly one test function | `research/modalities/emc_locoregional_eligibility.py` + `tests/test_locoregional_eligibility.py` | this lane | nothing | — | DEF | T |
| U51 | `W16e:293`, `W16f:277,297` | Six artifacts no longer reproduce; **"I did not decide which side is stale. That is the data owner's call."** Explicitly: do **not** add an identity test before the decision — a red guard is a broken gate | `research/modalities/emc-expression-panels.json` +5 | **data owner** | GEO series matrices via the Actions escape hatch | — | DEC+MEA | T |
| U52 | `W05g` routed, `W05h:228` | `e3-provenance-correction.json` does not parse; repair it, then re-walk. "Not run: I am read-only and it is not my file" | `research/modalities/e3-provenance-correction.json` | unassigned | nothing | — | DEF | **V** — `json.load` raises `JSONDecodeError: Expecting ',' delimiter: line 22 column 22 (char 984)` |
| U53 | `W05h` second | One row of seventeen missing the `overlap_risk` field its siblings carry | `research/modalities/emc-ipd-survival.json#/candidate_sources/0` | "whoever owns the schema rather than this lane" | nothing | — | DEF | T |
| U54 | `W20h` next action | The damage is one inherited sentence that 13 route sentences inherit | `emc-fourth-cohort-route-readout.json:14` | unassigned | nothing | — | DIS | T |
| U55 | `W10f:169`, next action | **"Corrected values, routed to the coordinator, NOT applied by me"**: strike the false clause at `emc-rt-bed-reappraisal.json:41`, append `⛔ SUPERSEDED` markers | `emc-rt-bed-reappraisal.json:41` +others | **coordinator** | nothing | — | DEF | T |
| U56 | `W15e:348`, `W15f` next action (=W24 D09/D10) | Route the **two ENTANGLED denominator records** as a single scope question — explicitly *not* a schema proposal. Constraint: any V5 edit must move `emc_radiotherapy_contradiction.py:273-275` **and** the artifact in one commit | `emc-radiotherapy-contradiction.json` + `care-delivery/emc-absence-claims-refuted.json` | the two artifact owners / sequencing driver | a wording judgement | — | DEC | T |
| U57 | `W15c:198-225`, `W15d` (=W24 R22) | Invariant **I6** — one line in lane 15's module. Its measured consequence: under a unit-requiring schema the registry supports **zero** fully-typed quantitative records (34/17/13 → 17/0/30) | lane-15 module | unassigned | — | — | DEC | T |
| U58 | `W15d:395` | Not-mine-and-stated-so: `denominator_means` already has three writers and a committed test that any I6 change would reach | `emc_care_delivery_evidence.py`, `emc_site_curation.py`, `emc_radiotherapy_contradiction.py` + a test | those owners | U57 | — | DEF | T |
| U59 | `W09b:277` | C3/C4 routed to `emc-surgical-quality.json`'s owner; C6 to `nr4a3_fusion_targets…` | those files | those owners | nothing | U02a says C5 was **mis-routed** as downstream of C3/C4 | DIS | T |
| U60 | `W13f` next action | Replace the check's heuristic aggregate discovery with an explicit committed manifest of pooled figures `(artifact, node path, member field)`; and: **six** `pool:false` sources, not one, sit inside committed pooled figures | registry/policy + the cross-file check | registry/policy owner | a decision | — | DEC+DEF | T |
| U61 | `W17f:745` (=W24 D16 partial) | Alignment contract **option (a) costed** at ~4 generator lines / +1 KB / +1 test and **routed to the coordinator for the ATR generator's owner**, conditional on a pinned-figure and views check; option (b) costed at **+74,454 bytes (+21.7 %)** and not recommended | ATR generator | coordinator → ATR generator owner | a decision; explicitly **not** to be bundled with U62 | — | DEC | T |
| U62 | `W17f` next action | Land `test_committed_welch_blocks_invert_to_their_own_rows.py` verbatim, then confirm `tier_budget` | `research/modalities/tests/` | **"whoever owns integration"** | write authority + tier budget | ⛔ with U64 | DEF | **V** — no welch-named file exists in that directory |
| U63 | `W17h:188`, next action | Land W17f's module **and** W17h's together → coverage from 21 blocks (0.81 %) to 1,13x blocks | same directory | integration owner | same | ⛔ with U64 | DEF | V |
| U64 | `W17i` next action | **"Land nothing new; consolidate."** Merge W17f's, W17h's and W17i's three modules into one | same directory | this lane | same | ⛔ **conflicts with U62 and U63 as written — 2 pairs** | DEC | T |
| U65 | `W17:273`, `W17b:513`, `W17d:736-737` (=W24 D16) | Promote `welch_df_identity.py` / `welch_variance_inversion.py` / `atr_point_verify.py` into the same directory. W17d adds: **no generator repair is warranted and it is not proposing one** | same directory | tooling | write authority + tier budget | overlaps U62–U64 | DEC | T |
| U66 | `W17h` follow-up (a) | Tighten `aso_delivery_antigen.py`'s self-consistency control from a flat `0.02` on `t` to the artifact's own half-ulp, plus a df check — **"the one place in the repository where a real gate is 40× looser than the data it reads"**; two lines | `aso_delivery_antigen.py` | module owner | PUB-ASO adjacency | — | DEF | T |
| U67 | `W27` R2/R3, next action | Ten Class A+B modules can adopt the whole-document comparison idiom 42 siblings already use, at **zero** test-function cost; start at `aso_delivery_antigen.py:838-839` and `emc_fourth_cohort_quant.py` | ten modules | "the module owners" | nothing | ⛔ **W27: "Not recommended: placing any new test in commit-loop before Option 1"** — conflicts with U31, U62, U63, U64 | DEF | T |
| U68 | `W27` next action | Resolve the 78 unclassified modules (22 Class D + 56 Class E) and publish the 130-module publish-vs-gate census | census | unassigned | nothing | — | MEA | T |
| U69 | `W11b` (=W24 R13) vs `W11d` next action | Place the source-index helper + tests. **W11b/W11c/W23**: the full pair at `scripts/`. **W11d**: *"place the 18-function pair plus D6 and D4 only, in `scripts/tests`, and stop there"* — 1466 → 1488/1500. And **W11d closes D1/D2/D3/D5 as "no viable home", D7/D8 declined on merits** | `scripts/source_reuse_index.py` (+tests) | **W11b as sole code owner** | W24 D18: the measured 1497+18=1515>1500 ceiling; three shortcuts explicitly refused | ⛔ **2 pairs** (W11d × W11b, W11d × W23) — and note the destination-path divergence W24 flagged (`research/tools/` in the bundle vs `scripts/`) is unresolved | DEC | **V** — `scripts/source_reuse_index.py` absent; `research/tools/` absent |
| U70 | `W11d:363` | `tier_budget.count_dir` counts non-recursively — a test in a subdirectory would be budgeted by nothing while still running on every push | `scripts/tier_budget.py` | "outside this lane" — unassigned | nothing | — | DEF | T |
| U71 | `W03d:305` | The `_load` misattribution: a missing joined screen is reported to the operator as something else | ASO screen loader | unassigned | nothing | — | DEF | T |
| U72 | `W20d:352`, §6 | Four label changes with exact current and proposed text. **"I relabelled nothing myself."** | probe/panel labels | unassigned | nothing | — | DIS | T |
| U73 | `W20g` next action | The smallest honest fix to the §3 defect is **a label change and one field, not a filter change** — explicitly disjoint from U40, lands whether or not U40 is accepted | probe denominator label | "whoever holds the module" | nothing | adjacent to U40, not conflicting | DIS | T |
| U74 | `W10c:60-64` (=W24 R26) | `mcp__PubMed__get_full_text_article` silently accepts a PMID as a PMCID and returns a different paper, no error, no warning | **tooling, not a repo file** | coordinator / tooling owner | nothing | — | DEF | T |

### Tier 4 — corrections whose only reader is the campaign's own artifacts

| # | Report:line | What it is | Target | Owner | Blocked | Class |
|---|---|---|---|---|---|---|
| U75 | `W23b:344` | One coordinator write: append a dated correction block carrying eight routed items; **two are new and not covered by W21b or W25** — `W23:195` and `W01f:89` | `WAVE-LOG.md` | coordinator | no | DIS |
| U76 | `W21c` next action | **Fix the campaign's dispatch text before dispatching anyone else** (the junction-source-absent standing fact), then append three corrections | dispatch text + reports | coordinator | no | DIS |
| U77 | `W21d` next action | Fix `W21b:145`'s table cell — "the last remaining source of the EGA defect, and it is one line" | `reports/W21b` | coordinator | no | DIS |
| U78 | `W07e` "flagged for the coordinator" | `W07:173` and `:290` still assert a refuted universal — "a two-line strike-through… it should not wait on another lane" | `reports/W07` | report owner | no | DIS |
| U79 | `W07f` next action | Focused correction to `W07e` §5.4 and its Axis-R row for PMID 27418251 (Morioka is 2 EMCS + 3 MCS, not EMC-only 5) | `reports/W07e` | coordinator | no | DIS |
| U80 | `W07g` next action | Correct `W07e` §5.5's two miscounted cells (8→7, 38→39); add a composition-provenance column | `reports/W07e` | lane owner | no | DIS |
| U81 | `W07h` next action | Amend `W07g:161` and `W07e:177-178` together — same defect at two removes | those reports | coordinator | no | DIS |
| U82 | `W08h` next action | Focused correction appended to `W08f` (per `CORPUS-CONTEXT.md` §4, not a new review round) | `reports/W08f` | coordinator | no | DIS |
| U83 | `W04e`, `W04f` next actions | Three narrow wording corrections + one denominator correction across `W04c:196-207` and `W04d`'s rows; `W04d` also asks the coordinator to reconcile two medians for one set | lane-4 reports | coordinator | no | DIS |
| U84 | `W10e` next action | Add the four `CLOSED-WORK`-only routes (Sunitinib's three institutional 403s, Wagner, Trabectedin/RT) to the reachability record | reachability record | coordinator | no | DEF |
| U85 | `W01f`, `W01g` next actions | Retire "44–63 obtainable" as a quotable figure; **one ruling** picking D2/D3/D4/D5 then applied to all five rows in one pass (consequence: a core of 4 to a core of 20) | lane-1 inventory | **lane owner** | a ruling | DEC |
| U86 | `W15b` first item | 71 identifiers now in `research/**/*.md` prose that no tracked `.json` anchors — "**Coordinator, before the next `preflight.sh`**" | tracked prose | coordinator | no | DEF |
| U87 | `W28` addendum | Re-check whether the six dead guards still match the text they were written against, in the same pass as U17 | guards | pin-registry owner | U17 | DEF |
| U88 | `W22b` next action | Collect the 21 named in-flight workers' response bodies before the VM is reclaimed, prioritised by `ts_last` | campaign state | coordinator | time | MEA |

### Tier 5 — measurement and retrieval requests

| # | Report | Request | Blocked on | Class |
|---|---|---|---|---|
| U89 | `W01`, `W01b` | Brenca 2019 deposit accession | **BLOCKED — 14 distinct routes, `curl: (56) CONNECT tunnel failed, response 403` / `EGRESS_BLOCKED`.** W01b's own headline: an independent group had to obtain a comparable dataset by formal request to journal editors | MEA |
| U90 | `W01e`, `W01f`, `W01h` | Identify inventory row 12 by an archive query; price the eight unmeasured rows' gene-space measurements | **Actions runner** (~15 min, shares a job with U89) | MEA |
| U91 | `W02b`, `W16f` | Commit `GSE24369_series_matrix.txt.gz` and `GSE4303-GPL3290_series_matrix.txt.gz` via the CI fetch path, re-run estimand C / the panels generator | **Actions runner.** W02g/W02h both state explicitly that naming the transcriptome-wide variant as a successor would be proposing a route already known closed | MEA |
| U92 | `W10b` | Oshiro 2000 full text (`PMID 11493979`) | **Actions runner** | MEA |
| U93 | `W10d:197` (=W24 D17) | Does an Actions-runner fetch of the Kawaguchi PDF count as a genuinely new route? | **a coordinator ruling.** ⚠ This is a question, **not an authorization** | DEC |
| U94 | `W20d:324`, `W20e:218` | Confirm the candidate sequence against the vendor TempO-Seq probe manifest | **recorded egress denial — not attempted, no route probed** | MEA |
| U95 | `W20f` next action | Run the patched `phase_map` at k=2 and report gene count | **Actions runner** | MEA |
| U96 | `W30:323` | Re-read `PMC4946242` Methods + Table 2 | **not blocked** — W07f proved it reachable at $0; W30 declined on scope | MEA |
| U97 | `W07b`, `W07e`, `W07f` | PMC full texts: cabozantinib `PMC8776602`, apatinib `PMC7237692`, four Group-I EMC-only cohorts, six remaining | reachable via PubMed MCP where a PMCID exists; **CI route for the rest** | MEA |
| U98 | `W07g` second, `W07h` | Six Group-I cohorts have no PMC full text and are **out of reach of the campaign's permitted route entirely**; `15920699` "belongs wherever retrieval is authorised" | no permitted route | MEA |
| U99 | `W04d`, `W04e`, `W04f` | PMID 19890812 full text | **"no viable retrieval successor… every remaining route is outside the permitted set or forbidden."** W04c's `PMC6449903` came back empty on two calls — a deposit- or tool-side gap | MEA |
| U100 | `W08c`, `W08d`, `W08g`, `W08h` | The 5 unavailable-abstract / missing-value records | **closed at source; all five yielded no value.** No further recovery successor exists in the lane | MEA |
| U101 | `W18`, `W18b` | Application of the selection estimator to real EMC data | **deliberately not run** — at k=3 the bound spans 0.204–0.460 and is uninformative. ⚠ `W18b:301,637`: a registry re-verification read was **blocked by the auto-mode classifier and not routed around** | MEA |
| U102 | GSE243553 marker BEDs | 403 CONNECT policy denial (=W24) | **BLOCKED**, and adjacent to the HELD W25 material — not touched | MEA |

---

### Totals

Counting rule as defined in Method. Every total is over the **150 reports at `215ed8e7`**, minus W25 (HELD/EXCLUDED).

| Quantity | Count | Note |
|---|---|---|
| **Routed-but-unlanded items** | **102** (U01–U102) | 74 changes/decisions on tree targets, 14 campaign-artifact corrections, 14 measurement requests |
| By class | **DEF 41 · DIS 21 · DEC 26 · MEA 14** | rows carrying two classes counted at their primary |
| **Distinct target files/paths** | **51** | 7 in `systems/graph/` or `systems/views/`; 3 active-manuscript or pin-registry; 5 gate/validator; ~26 generators and artifacts; ~10 campaign-report or coordination targets |
| **Items naming an owner** | **63 name an owner *class*** (registry owner, preflight owner, PUB-ATR/PUB-ASO manuscript owner, graph owner, data owner, coordinator, module owner, lane owner). **0 name an individual person.** | **39 are effectively unassigned** — "whoever owns the gate", "whoever owns integration", "the lander", or no owner named at all |
| **Blocked on a denied or absent source** | **9** (U89, U91, U92, U94, U95, U98, U99, U102, and U51's GEO half) | Of these, **5 would be unblocked by one Actions-runner authorization** (U90, U91, U92, U95, and U51). **2 are not actually blocked** and were declined on scope, not access (U96, U97-in-part) |
| **Conflicting pairs** (two reports proposing changes to one target that cannot both land as written, per the reports' own words) | **16 pairs across 6 targets** | see below |

**The 16 conflicting pairs, by target:**

| Target | Pairs | Nature |
|---|---|---|
| `emc_fourth_cohort_quant.py` | 2 | R07×R08 (⛔ true either/or, W24 D01); C3/U39 × R07's hunk (textual, `W24b:243`) |
| `scripts/preflight.sh` (locale) | 3 | W12b×W12c, W12b×W12d, W12c×W12d |
| `research/modalities/tests/` | 2 | W17i("merge into one")×W17f, W17i×W17h |
| gate-row additions vs W27's hold | 5 | W27×W17f, W27×W17h, W27×W17i, W27×W14e(U31), W27×W13g(U28) — W27: "Not recommended: placing any new test in commit-loop before Option 1" |
| source-index placement | 2 | W11d×W11b, W11d×W23 |
| `systems/graph/publications.json` C5 | 1 | W09d("not written, not packaged")×W09e("full correction diff supplied") — a status disagreement |
| `emc_mortality_decomposition.py` | 0 conflicts, **3-way sequencing** | W06d, W14, W06f — W24 saw only two of the three |

**Complementary, explicitly not conflicts:** U19→U20 (ordered), U15+U16+U17 (three reports, one pin file, land as one edit), U13→U14 (ordering constraint stated by W17g), U40 vs U73 (W20g states its fix is disjoint from W20f's).

### Ranking — what a wrong or unmade change would reach

Rank by reach, then by whether the reach is verified:

1. **`systems/graph/*.json` (U01–U09) — highest.** Reach **VERIFIED IN TREE**: `CLAUDE.md` §7 names `systems/graph/*.json` as owning model state and `systems/views/` as generated; all three graph files exist at HEAD; `W09e`'s own regeneration proof (transcribed, not re-run) measured **5 lines in 5 files** moving from one clause, and `W09g` measures its correction rendering into **6 view lines across 5 files**. A wrong change here is transcribed automatically into the generated layer.
2. **Active manuscript prose (U13, U14) — VERIFIED.** `sed -n '761p'` shows the disputed `0.41× that standard error` still standing in `emc-atr-vulnerability-assessment.md` at HEAD. A wrong or unmade change here is read by a human reader of a paper.
3. **The clinical registry (U19–U25) — VERIFIED absent, protected, and byte-pinned.** `nUnit`/`denomNote`/`periodBasis` counts are all **0**; `systems/POLICY-evidence.md` and `CLAUDE.md` §7 protect the file; `W16c:204` (transcribed) prices it as byte-pinned inside a DOI-minted deposit. Highest cost-to-change in the campaign.
4. **The commit gate (U26–U36) — VERIFIED.** Neither locale variable is present; neither proposed gate row is present. But note W24's own gate-reachability finding, which I did not re-derive: **no repair target in the index is a member of the 18-row `--check` loop**, so fixing a guard here enforces nothing on its own.
5. **Pin registry (U15–U17) — VERIFIED partially.** `pinned-figures.json` has 99 `artifact_figures`; `fusion-junction-neoantigen-paper` is absent from `targets[]`. Reach is manuscript figures, mediated by a validator.
6. **Generators and artifacts (U37–U74) — mostly TRANSCRIBED**, with four spot-verifications (U39 drift tuple, U41/U43 absent fields, U52 unparseable JSON, U69 absent files). Reach is whatever consumes each artifact, which I did not enumerate per file.
7. **Campaign-report corrections (U75–U88) — lowest reach by construction**: read only by their own artifacts and by indexes like this one. I did not verify these in the tree; they are report-internal.

**Rankings I verified against the tree:** ranks 1–5 and the four spot-checks in rank 6, by the commands in Validation evidence. **Rank 6's remaining rows and all of rank 7 are transcribed only**, ordered by the reports' own descriptions of their targets.

---

### The question the index exists for

**Is the unlanded surface growing faster than it is being resolved? Yes — and by the strongest available margin, because the resolution rate I could measure is zero.**

- **Growth, measured.** W24 indexed 92 reports at `4d950cf0` (02:53Z) and produced 26 repair rows + 20 decisions. At `215ed8e7` (03:31Z) the corpus is **150** reports; by `1c9d8278` (03:36Z) it is **157**. In ~40 minutes the corpus grew by ~65 reports and this index carries **102** routed items — roughly **4× W24's 26 repairs**, with **16 conflicting pairs against W24's 3 flags**, and three conflict clusters that did not exist when W24 ran (`W20g`/`W20h` making `emc_fourth_cohort_quant.py` a four-change/five-report target; `W17h`/`W17i` making `research/modalities/tests/` a three-module/one-directory dispute; `W11d` re-shaping the source-index placement W23 and W24 had framed differently).
- **Resolution, measured.** I checked **eleven** of W24's routed items against the tree at `215ed8e7`. **Every one is still unlanded**: `nUnit` 0, `denomNote` 0, `periodBasis` 0, `PYTHONUTF8` 0, `PYTHONIOENCODING` 0, `quotability` 0, `smallest_coherent_share_pct` 0, `probe_counts_sha256` absent from the drift tuple, `scripts/source_reuse_index.py` absent, no welch test in `research/modalities/tests/`, ATR `:761` unchanged. **Landed count over the interval: 0 of 11 checked.**
- **What *did* close were questions, not changes.** W12e and W12f closed two named UNKNOWNs under the locale decision without landing it. W24b and W24c narrowed R07/R08 to "size, test count and memory cost" without picking one. W11d answered the tier-hosting question with a smaller placement — and thereby created a new conflict with the shape W11b/W11c/W23 had proposed. W17d determined that **no generator repair is warranted** and refused to propose one, which is the one genuine net *reduction* of the surface I found. Meanwhile W22b's next action is a reminder that **21 worker bodies were still uncollected** — so the true surface is larger than 102.
- **One correction to W24 that this run establishes by execution:** W24's D06 rests on the premise that the committed registry has **no `evidenceQuestions` at all**. At `215ed8e7` it is present at `research/data/emc-clinical-registry.json:1707` and is a top-level key. I do not adjudicate whether the validator rule at `validate-registry.mjs:124` is satisfied — only that the premise is false at this HEAD.

**Which handful would close the most.** Six acts, none of them a repair I am performing, ordered by items closed per unit of authority:

| Act | Closes | Why it is the most efficient |
|---|---|---|
| **1. Rule on the preflight locale variable** (U26/U27) | 5 reports (W12b, W12c, W12d, W12e, W12f) → **2 items, 3 conflict pairs** | One line. Evidence chain complete and internally consistent; **no missing input**; two lanes have already packaged it and asked for nothing but the choice |
| **2. Pick R07 or R08 and land it with C3** (U37/U38/U39) | 5 reports (W14c, W14d, W24b, W24c, W20h) → **3 items, 2 conflict pairs** | The single most contended file in the campaign — four routed changes from five reports. W24b has already reduced the choice to a textual-ordering fact |
| **3. Rule once on `research/modalities/tests/`** (U62/U63/U64/U65) | 5 reports (W17, W17b, W17d, W17f, W17h, W17i) → **4 items, 5 conflict pairs** | One destination-shape ruling — three files or one merged module — plus the tier-budget authority. It also settles W24's D16 |
| **4. Land W09g + W09f:286 as one atomic commit with `--write-views`** (U03) | **1 item, but the highest-reach one in the index** | Verified Tier 1; W09g states it is the only item both FALSE and rendered into 6 view lines across 5 files; zero missing input. Do U02/U02a next, since it is a status disagreement, not a scientific one |
| **5. Decide the registry byte-pin** (U25, then U19+U20 as one ordered commit) | **7 registry items (U19–U25) unblock behind one decision** | Every registry item shares one blocker — the DOI-minted byte pin — so this is one judgement standing in front of seven changes, not seven judgements |
| **6. Coordinator: append W23b's eight-item correction block to `WAVE-LOG.md`** (U75, U76, U77) | **~6 Tier-4 items at one write** | Pure bookkeeping, no retrieval, no analysis; and W21c's half of it stops the dispatch text from seeding the same error into every future worker |

Together those six close or unblock **roughly 28 of the 102 items and 10 of the 16 conflict pairs**, and five of the six need no retrieval at all. **The single largest lever outside them is one Actions-runner authorization**, which would unblock 5 measurement requests (U90, U91, U92, U95, U51) — but that is a grant only the user or coordinator can make, and it must not be confused with U93, which is the *question* of whether such a fetch counts as a new route rather than an authorization to make one.

---

## Validation evidence

All `RUN` by me. Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, Claude Code 2.1.42, `python3` 3.11 stdlib only, cwd `/home/user/Rare-cancers`, **no network**, no paid API, no GPU, no repository write, no git write.

| # | Command | Exit | Key verbatim output |
|---|---|---|---|
| V1 | `date -u`; `git rev-parse HEAD`; `git status --porcelain` (start) | 0 | `Tue Sep  8 03:31:46 UTC 2026`; `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1`; *(empty)* |
| V2 | `env \| grep -i -E "model\|claude"` | 0 | quoted in full under Worker; **no variable names a model** |
| V3 | `ls reports \| wc -l` (start / end) | 0 | `150` → `157` |
| V4 | routing-marker `grep -c` census over 149 reports | 0 | ranked list, top non-W24 entries `11 W19b`, `10 W18b`, `10 W06b`, `9 W13c`, `9 W13b` |
| V5 | path × routing-marker co-occurrence grep over 149 reports | 0 | the target-file column of the tables above, each row carrying its own `report:line` |
| V6 | `awk` extraction of `## Next concrete action` over ~100 reports | 0 | the residual-per-report input to Tiers 1–5 |
| V7 | existence test on 25 target paths | mixed | `EXISTS` ×22; **`ABSENT`**: `scripts/source_reuse_index.py`, `research/manuscripts/nr4a3-fusion-transcriptional-output.md`, `research/data/aso-per-junction-table.json` (the latter two exist under different paths — see Limitations) |
| V8 | `grep -c` unlanded-status sweep | 0/1 | `"nUnit"` → **0** · `denomNote` → **0** · `periodBasis` → **0** · `PYTHONUTF8` in preflight → **0** · `PYTHONIOENCODING` in preflight → **0** · `emc_rt_bed_reappraisal` in preflight → **0** · `emc_relative_survival` in preflight → **0** · `quotability` → **0** · `smallest_coherent_share_pct` → **0** · `argparse` in `emc_relative_survival.py` → **0** · welch files in `research/modalities/tests/` → **0** |
| V9 | `python3 -c "json.load(open('research/modalities/e3-provenance-correction.json'))"` | non-zero | `json.decoder.JSONDecodeError: Expecting ',' delimiter: line 22 column 22 (char 984)` — **U52 confirmed** |
| V10 | `grep -n 'probe_counts_sha256\|gene_counts_sha256' emc_fourth_cohort_quant.py` | 0 | `819: out["probe_counts_sha256"] = …` · `832: out["gene_counts_sha256"] = …` · `941: … "gene_counts_sha256")` — **written but absent from the drift tuple; U39 confirmed** |
| V11 | `python3 -c "json.load(open('research/manuscripts/pinned-figures.json'))"` keys | 0 | `['_README','targets','_marker_note','supersession_markers','derivations','artifact_figures','table_completeness','superseded','subset_checks','_artifact_figures_note']`; `artifact_figures n= 99`; `fusion-junction-neoantigen-paper` → **0** |
| V12 | `python3 -c "…emc-clinical-registry.json…"` top-level keys | 0 | `[... 'questionsForOncologist', 'evidenceQuestions']`; `has evidenceQuestions: True`; `grep -n` → **`1707:  "evidenceQuestions": [`** — **contradicts W24 D06's premise** |
| V13 | `sed -n '761p' research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` | 0 | ``…clears it by **0.0155, 0.41× that standard error**,`` — **U13 unlanded** |
| V14 | `sed -n '6399p;6505p' systems/graph/routes.json` | 0 | two byte-identical `"contribution"` clauses — **U06's target confirmed** |
| V15 | `grep -n 'G3\|def check_views' systems/systems_check.py` | 0 | `4535:def check_views(g, f)` and **no `G3`** — U11 confirmed |
| V16 | `git log --oneline 215ed8e7..HEAD`; `git diff --name-only 215ed8e7 HEAD \| grep -v opus-capacity` | 0 / 1 | `1c9d8278 campaign briefs…`, `793f63cb campaign: collect W01i, W33, W06h, W09h, W03f, W14e, W29b, W35`; **no output** — nothing outside the campaign directory changed, so all anchors hold |
| V17 | `date -u`; `git rev-parse HEAD`; `git status --porcelain \| wc -l`; `rm -rf /tmp/claude-0/w36` (end) | 0 | `Tue Sep  8 03:36:25 UTC 2026`; `1c9d827870599576c0c027a9134363d59456fd04`; `0`; `ls: cannot access '/tmp/claude-0/w36'` |

**`PROPOSED (NOT RUN)` by me:** applying, testing, gating, sequencing or adjudicating **any** item above; running `scripts/preflight.sh` (dispatch forbids it) or any pytest; any network call, MCP call or retrieval; reading the frozen corpus; reading W25 or anything derived from it; opening the seven reports added mid-run.

---

## What I read versus only counted

- **Read in full:** `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `SAFETY-EVENTS.md`, `reports/W24-repair-routing-index.md` (all 310 lines).
- **Read in substantial part** (the routing-bearing sections and/or the full `Next concrete action` block, extracted verbatim, ≥1 named section each): W01, W01b, W01f, W01g, W01h, W02b–W02h, W03b–W03e, W04b–W04f, W05, W05b, W05d–W05h, W06b, W06d–W06f, W07b–W07h, W08c–W08h, W09b–W09g, W10b, W10d, W10e, W10f, W11, W11b, W11d, W12, W12b, W12e, W12f, W13d–W13g, W14, W14b, W14c, W14d, W14e, W15b, W15d, W15e, W15f, W16b, W16c, W16d, W16e, W16f, W17b, W17d, W17f, W17h, W17i, W18, W18b, W19, W19b, W19g, W19h, W20d–W20h, W21c, W21d, W22b, W23b, W24b, W24c, W26–W31. **That is ~95 of the 150.**
- **Matched by grep line only, never opened as prose:** the remainder — approximately 25 reports whose only appearance above is as a marker count or a transcribed anchor from another report (including W13, W13b, W13c, W15c, W17c, W17e, W17g, W23, W21, W21b, W09c, W06d's patch body, W12c, W12d, W14's diff bodies — for these I carry W24's transcription rather than re-reading, and say so).
- **Not touched at all:** W25 (**HELD/EXCLUDED** by the safety receipt — scope UNKNOWN, not routed around), and the seven reports added after `215ed8e7` (**W01i, W33, W06h, W09h, W03f, W29b, W35**).
- **Verified against the tree (rows marked `V`/`V*`):** U06, U11, U13, U15, U17, U19, U20, U21, U22, U26, U28, U29, U39, U41, U43, U52, U62, U69 — 18 of 102, by the commands in V7–V15. **Everything else is transcribed from report bodies I did not re-execute.**

---

## Limitations

- **This is a map of what reports say, not a verification that they are right.** Except for the 18 `V`-marked rows, every exit code, negative control, measurement, cost and blast radius quoted above is **transcribed from a report I did not re-run**. A worker report is not a test result.
- **I did not read ~25 of the 150 reports as prose**, and my marker greps keyed on a fixed vocabulary (`routed`, `not applied`, `owner's call`, `PROPOSED (NOT RUN)`, `coordinator decision`, path × marker co-occurrence, `Next concrete action`). **A routed item phrased outside that vocabulary is invisible to this index, and its absence is UNKNOWN, not evidence it does not exist.**
- **The corpus moved under me and is already ahead of this index.** Seven reports arrived mid-run and are unindexed; `W22b` records **21 worker bodies still uncollected**. The true surface is larger than 102 and this snapshot is stale on delivery.
- **Two target paths named in reports do not resolve as written.** `nr4a3-fusion-transcriptional-output.md` (U08) and `aso-per-junction-table.json` (W24 R25) are `ABSENT` at the paths their reports give; the tree carries `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-*`. **I did not determine which path is intended** — that is the owner's, not mine.
- **My totals depend on my counting rule**, stated in Method. A different rule (per-hunk, or per-report) gives a different number. The class assignment (`DEF`/`DIS`/`DEC`/`MEA`) is mine, derived from each report's own words; where a row carries two classes I named the primary and said so.
- **I adjudicated nothing.** The one place I contradict a prior index (U22, `evidenceQuestions`) is a filesystem fact shown in full, not a ruling on the validator rule, the registry's intent, or W13's finding.
- **The growth-vs-resolution answer rests on 11 spot-checks, not on all 102 items.** "Zero landed" is a measured statement about those eleven; the other items' landing status is UNKNOWN unless marked `V`.
- **I did not read the frozen corpus**; every corpus-dependent statement is SECONDARY, transcribed from W21/W21b/W21c/W21d/W23b.
- **No clinical claim of any kind is made or implied.** This index covers tooling, guards, provenance contracts and evidence routing. There is no wet lab; nothing here bears on EMC efficacy, safety, selectivity, therapeutic window or clinical readiness, and no computational result in this campaign could establish any of those.
- **Blocked routes are recorded, never probed.** I made zero network calls. Listing a blocked input is not a suggestion to retry it; U93 is a coordinator *question*, not an authorization. `W18b:301,637` records a **classifier permission denial on a registry read** which was not routed around — I record it and route nothing from it.

---

## Stop condition

**Set up front:** return the moment every routed-but-unlanded item recoverable by systematic marker extraction across all 150 reports at the pinned HEAD is enumerated with report and line, target, owner, blocker, conflict and class; the ranking is stated with its verified subset named explicitly; the five totals are reported; and the growth-versus-resolution question is answered from measured evidence — at roughly 40 tool calls / 40 minutes, without padding, and without performing, adjudicating or deciding any item.

**MET.** 102 items across 51 distinct targets, 16 conflicting pairs across 6 targets, five tiers with the verified subset named, 17 validation rows, and the growth answer grounded in 11 tree-verified spot-checks showing zero landings. Scratch deleted. Returning immediately.

---

## Tool-call and wall-clock count actually used

**27 tool calls** (all `Bash`; every one a read, `grep`, `awk`, `sed`, `ls`, read-only `git`, or `python3 -c` JSON read — plus the single `rm -rf` of my own scratch directory outside the repository). **Wall clock 4 min 39 s** (`03:31:46Z` → `03:36:25Z`), plus the final `ls`/`git log` check. Well inside the ~40-call / ~40-minute target; I stopped on the condition, not the budget.

---

## Next concrete action

**One successor, mechanical, needing no missing input and no decision: verify the unlanded status of the remaining 84 items against the tree, the way I verified 18.** For each U-row marked `T`, run the one grep or `python3 -c` that would show whether the proposed field, line, row or file is present at HEAD, and re-mark it `V`, `V*` (landed, or the report's premise is false) or `UNKNOWN` (not checkable by inspection). That converts this index from a map of claims into a measured backlog and — critically — gives the campaign its **first real denominator for the resolution rate**, which right now rests on eleven spot-checks. It is bounded (roughly 84 greps), needs no network, no owner authority and no adjudication, and it would immediately surface any item that has quietly landed since its report was written, as U22 did.

**A second, smaller successor if the coordinator wants it separated:** index the seven reports added after `215ed8e7` (`W01i`, `W33`, `W06h`, `W09h`, `W03f`, `W29b`, `W35`) and fold them into Tiers 1–5. They are unread by any index, and on this campaign's observed rate they carry roughly four to seven further routed items and at least one new conflict.
