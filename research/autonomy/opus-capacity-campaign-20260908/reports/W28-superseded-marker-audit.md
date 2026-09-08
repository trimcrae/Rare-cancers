<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:27:23Z UTC
     agent id a6a1b65b4de0c424e ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a6a1b65b4de0c424e.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

## Worker

**W28**, lane: retention-and-pinned-quantity integrity audit, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions only. The coordinator must extract the served model from the transcript.

**Write isolation honoured.** Nothing written under `/home/user/Rare-cancers`. No git write operation. All scratch execution under `/tmp/claude-0/w28/`. `scripts/preflight.sh` not run. No network, no paid API, no GPU spend.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:13:48 UTC 2026` | `Tue Sep  8 03:23:22 UTC 2026` |
| `git rev-parse HEAD` | `98a0833f1ede2cf9cef13790388260567a32e868` | `6552a6c8d35158858b4b9ed3846b8a276032873a` |
| `git status --porcelain` | 8 untracked campaign report `.md` files, no tracked modifications | empty |

**HEAD moved under me.** `git diff --name-only 98a0833f..HEAD` returns 32 files, **all** under `research/autonomy/opus-capacity-campaign-20260908/` (worker reports, `SAFETY-EVENTS.md`, W25 executed artifacts). **None of them is `pinned-figures.json`, a manuscript, a preregistration, `systems/graph/`, or any of the 29 linter targets.** Everything I measured is unchanged. The one drift: my tree-wide marker enumeration ran at `98a0833f` and therefore does not include markers inside the ~24 campaign reports collected after it; the tracked-repository denominators below are unaffected.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0), model-relevant lines verbatim; the long `no_proxy` / `NO_PROXY` / `npm_config_noproxy` / `GLOBAL_AGENT_NO_PROXY` / `JAVA_TOOL_OPTIONS` proxy lines are elided as marked and nothing else removed:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=…  [elided, proxy list]
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
GLOBAL_AGENT_NO_PROXY=…  [elided, proxy list]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=…  [elided, proxy/truststore]
NO_PROXY=…  [elided, proxy list]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=…  [elided, proxy list]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

## Question

Does the repository's standing superseded-and-retained discipline actually hold in the tree — do retention markers carry the quoted old text, the replacement, and a date/commit; do `pinned-figures.json`'s entries still agree with the files they pin; does a value ever change in current prose with neither a marker nor a registry entry; and has any correction been applied *inside* a preregistration?

It is open because the discipline is enforced by two things that do not overlap: `lint_consistency.py` (machine, but scoped to **29 declared target files** out of **7,741 tracked**) and prose convention (unscoped, unenforced). Nobody had measured the gap between them.

## Prior-work check

```
git ls-files | grep -i -E "prereg|pre-reg"                              → 13 files
grep -rc -i -E "supersed" --exclude-dir=.git .                          → per-file counts
git ls-files | rg -i "pinned|retention"                                 (via Glob/Grep equivalents)
```

Read `CLOSED-WORK.md` in full. Nothing there closes this question: the closed list covers scientific gates (Davis, Hofvander, Brenca, promoter transfer, pazopanib/sunitinib/CTARC source recovery, registry ICD-O), the NR4A Perspective refusal, and lane-11 source-index ownership. None is a retention/pinned-quantity integrity audit.

Read `reports/W09f-publications-false-absence-audit.md` R.3 as instructed. It establishes (a) the retention form in use — `⚠ Superseded, retained (rule 1.2): "<quoted old text>"` followed by the replacement — and (b) that R.3's own restatement is a **proposal, not applied**, so a bare grep for the superseded `publications.json:305` sentence fires on W09f's retained quotation of it. I confirmed this behaviour and excluded W09f's own quotations from being read as tree defects. I did **not** apply R.3 or any other correction.

Nearest neighbours I am not replaying: **W09b** (boolean JSON absence claims), **W09f** (prose absence claims in `publications.json`), **W09c** (artifacts contradiction package). All three audit *claim truth*; none audits *retention mechanics* or the pinned-figures registry.

## Method and inputs

- Live cloud checkout `/home/user/Rare-cancers`, HEAD `98a0833f…` at start. I did **not** read the frozen corpus at `/tmp/claude-0/frozen-corpus/`; every finding here is from the live checkout, and I record that choice per COMMON-BRIEF §5.2.
- `research/manuscripts/pinned-figures.json` (2,050 lines; keys `targets` 29, `artifact_figures` 99, `superseded` 81, `derivations` 1, `table_completeness` 1, `subset_checks` 1, `supersession_markers` 35).
- `research/manuscripts/lint_consistency.py` (648 lines; verified read-only — `grep -n "open(.*[\"']w|\.write_text|--write"` returns no write site; its only CLI flags are `--json` and `--repo`).
- Scratch scripts I wrote and ran under `/tmp/claude-0/w28/`: `scan.py`, `classify.py`, `classify2.py`, `pin.py`, `sup.py`, plus two inline heredocs. Python 3 as shipped in the container.
- Marker definition used: a line containing **both** a `supersed*` token and a `retain*` token, over all tracked files plus the untracked campaign reports, skipping `.git`.

## Result

### Part 1 — retention markers: 1,479 markers across 464 files; the quoted old text is nearly always there, a date or commit reference is missing in a third

**Honest denominator.** Tree-wide, `supersed*` (case-insensitive) appears on **10,106 lines**, but that number is worthless as a marker count: **7,089 of them are JSON *field names*** in four MD artefacts — `nr4a3-orientation-basins.json` alone carries 924 `"min_linker_atoms_relaxed_superseded"`, 576 `"fraction_reachable_by_linker_atoms_relaxed_superseded"`, 576 `"fraction_reachable_at_gate_relaxed_superseded"` and 348 `"max_fraction_reachable_at_gate_relaxed_superseded"` keys, and `aso-gap-length-tradeoff.json` carries 286 `"_superseded_locus_counts_from_the_old_parser"`. Those are data columns, not retention markers.

Requiring `supersed*` **and** `retain*` on the same line gives the working denominator: **1,479 markers in 464 files**. The variant spellings I found and folded in (all case-insensitive): `Superseded, retained`, `SUPERSEDED, RETAINED`, `superseded-and-retained`, `Superseded, retained (rule 1.2)`, `Superseded, retained verbatim and quotable`, `Superseded in turn, retained`, `SUPERSEDED … RETAINED:` split across a colon-terminated line, `Superseded reasoning retained below`, `⛔ Superseded 2026-08-03. Retained, not current.`, and `superseded_retained` / `⛔_superseded_retained` as JSON keys. `pinned-figures.json` additionally declares its own list of **35** `supersession_markers` tokens for the linter.

Top-loaded files: `nr4a3-program-map.md` 103, `systems/graph/routes.json` 81, `research-ledger.json` 45, `fusion-junction-aso-working-record.md` 38, `fusion-junction-aso-preprint-checklist.md` 32, `emc-fusion-partner-correction-register.md` 20.

Screen results against the three required elements (marker line + next 2 lines for the quotation; ±3/+4 lines for date/commit):

| element | present | absent |
|---|---|---|
| quoted superseded text | **1,449 / 1,479 (98.0 %)** | 30 |
| replacement | 1,106 / 1,479 (74.8 %) — **screen unreliable, see below** | — |
| date **or** commit reference | **986 / 1,479 (66.7 %)** | **493 (33.3 %)** |

`PRIMARY` for the counts (I ran the scan); `PREDICTION` for nothing here.

**The replacement column must be discounted.** I hand-read a seeded random sample of **20 markers** with full ±3-line context. In every one of the real markers, the replacement *is the surrounding current prose* — the convention is "correct current prose directly" (CLAUDE.md §1), so the marker quotes the retired text and the live sentence next to it is the new value. A regex looking for `now reads` / `replaced by` therefore under-counts by construction. **On hand-check, 20/20 real markers carried a recoverable replacement. I report the automated 373 "missing replacement" as a screen artefact, not a defect count.** Example, `research/manuscripts/degrader/nr4a3-inverse-linker-design-2026-07-25.md:825`:

> `categorical_verdict.by_scope[*].by_linker_atoms`. *Superseded, retained: the pilot pair **0.081 at 16** and **0.258 at 20**, registered as `paralogue_collision_pilot_5657`.* **The ordering, and every conclusion drawn from it, is unchanged — the curve is the same shape and steeper.**

**The 30 "missing quotation" hits are also mostly screen artefacts.** Four I read are not markers at all: `research/modalities/tests/test_design_brief_asymmetric.py:51` is a *test asserting* retention (`"the retired framing must be RETAINED as superseded, not silently dropped"`); `research/autonomy/priority.py:879` and the `.github/workflows/step1-fanout-supervisor.yml:279-281` pair are commentary about retention. `WAVE-LOG.md:102` states the retention in prose without quoting ("The original text is retained above so the history reads honestly; this section supersedes it") — the old text is genuinely above it, so the requirement is met by layout rather than by quotation.

**The one element that is genuinely and reproducibly missing is the date or commit reference: 493 markers (33.3 %) carry neither anywhere in their immediate context.** Verified by hand from the sample:

| file:line | quoted | replacement | date/commit |
|---|---|---|---|
| `research/autonomy/sprint-2026-09-01/S53-HYPOXIA-BACKGROUND-READ.md:369` | yes | yes (preceding sentence) | **none** |
| `systems/views/plan.md:1070` | yes (`4090 755.36 / 4080 703.51 / 3090 359.36`, `2.10×`) | yes | **none** — defers to "Appendix T says what retired them" |
| `research/manuscripts/aso/fusion-junction-aso-working-record.md:152` | yes | yes | **none** |
| `research/manuscripts/aso/fusion-junction-aso-working-record.md:1579` | yes | yes (`§3a-octies, §3a-nonies`) | **none** |
| `research/manuscripts/aso/fusion-junction-aso-preprint-checklist.md:926` | yes (`47%`, `4% to 100%`) | yes | **none** |
| `research/manuscripts/degrader/nr4a3-degrader-selectivity-architecture.md:195` | yes | yes | **none** |
| `research/manuscripts/degrader/nr4a3-inverse-linker-design-2026-07-25.md:825` | yes (`0.081 at 16`, `0.258 at 20`) | yes | **none** |
| `research/modalities/fet_ddr_axis_scan.py:46` | yes | yes | **none** |

Files with the most date-less markers: `nr4a3-program-map.md` 28, `systems/graph/routes.json` 19, `fusion-junction-aso-working-record.md` 17, `emc-fusion-partner-correction-register.md` 10, `cancer-modality-census.md` 10.

**Honest scoping of that finding.** CLAUDE.md §1 says *"Correct current prose directly; preserve preregistrations and record changes to pinned quantities in `research/manuscripts/pinned-figures.json`."* It requires a date on **status measurements**, not on every retention marker. So the 493 date-less markers are a gap against **the three-element criterion this audit was given**, and they do degrade traceability — but I found **no written repository rule that they violate**. Whether to require a date is a decision, not a defect I can assert. `UNKNOWN` whether any of them was intended to carry one.

### Part 2 — pinned-figures.json: 181 checkable entries, zero disagreements

`lint_consistency.py` on the live tree:

```
lint_consistency: 0 ERROR across 29 target file(s)
EXIT=0
```

I did not rely on that alone. I re-derived the `artifact_figures` check independently (`/tmp/claude-0/w28/pin.py`), resolving each entry's dotted `key` into its `artifact` JSON and looking for the resulting value in every `must_appear_in` document:

| check | result |
|---|---|
| `artifact_figures` entries | **99** |
| artifact file missing or unparseable | **0** |
| `key` path no longer resolves in the artifact | **0** |
| `must_appear_in` document missing | **0** |
| pinned value vs. value in the document | **99 / 99 agree** |
| `targets[]` files that no longer exist | **0 / 29** |
| `superseded[]` patterns that fail to compile | **0 / 81** |
| `derivations[]` / `table_completeness[]` / `subset_checks[]` | 1 / 1 / 1, all clean under the linter |

`PRIMARY`. Total entries checked: **99 + 81 + 1 + 1 + 1 = 183**, plus 29 target paths.

Two entries initially flagged by my checker were **false alarms of my own renderer, and both actually agree**: `biomarker_guardians_t_gpl6244` pins `-4.568` and `biomarker_guardians_t_gpl3290` pins `-2.538` from `research/modalities/census-route-expression-grading.json`; both declare `"format": "{:.2f}"`, and `research/manuscripts/dependency/emc-biomarker-selected-classes.md:194` prints them correctly as `(*t* = −4.57 and −2.54)`. My substring search missed them only because the document uses U+2212 MINUS SIGN rather than ASCII hyphen. **Agreement, not disagreement.**

**This part is clean and that is the finding.** Every pinned quantity still agrees with the file it pins; no pinned target has gone missing.

One structural weakness inside the registry, quoted rather than asserted. `pinned-figures.json`'s own `_README` says:

> **KEEP PATTERNS TIGHT.** A linter that flags true statements gets ignored, which is worse than no linter (lint_claims.py's founding lesson). **Prefer a multi-token pattern over a bare number.**

Entry `valb_rung_band_8_78_22_28` has `"pattern": "8\\.78|22\\.28"` — a bare-number pattern with no token context. Across the 6,927 non-target tracked files it matches **632 times**. It is harmless today only because the linter never looks outside `targets[]`. `SECONDARY` (a reading of the registry against its own stated rule).

### Part 3 — the inverse defect: the prescribed method is not executable here, and the content-based substitute found one concrete case

**The `git log --follow` method does not work on this checkout, and this is a hard fact, not a difficulty.** The visible history is **340 commits spanning 2026-09-04 → 2026-09-08**, and essentially all of them are campaign-report collection. All 7,741 tracked files entered at the history root. `git log --follow` across all 29 pinned-quantity target files returns **31 commit-touches in total** — 27 of the 29 files have **exactly one** commit each; `CLAUDE.md` and `.claude/skills/repo-gates/SKILL.md` have two:

```
targets: 29   total commit-touches: 31
   2  .claude/skills/repo-gates/SKILL.md
   2  CLAUDE.md
   1  STRATEGY.md
   1  research/manuscripts/nr4a3-program-map.md
   …  (25 further files at 1 each)
```

Every pinned-quantity correction the documents themselves describe — dated 2026-06-25, 2026-07-25, 2026-07-27, 2026-08-15, 2026-08-22, 2026-08-28 — happened **before this history begins**. `UNKNOWN`: whether any of them was accompanied by a `pinned-figures.json` entry in the same commit cannot be determined from this checkout. I did not fabricate a history sweep in place of that.

**Content-based substitute, which does work.** `superseded[]` records an old value that "may still appear … but ONLY on a line that marks it as superseded." I compiled all 81 patterns, found the **23** that match nowhere in the 29 scanned target files, and ran those 23 across the **6,927 tracked non-target files** (`.md`, `.json`, `.py`, `.txt`, `.yml`, `.sh`, under 6 MB), checking each hit against the registry's own 35 clearing markers in its own declared window.

Most hits are explainable and I discard them: matches inside `pinned-figures.json` itself (it is the registry), inside `lint_claims.py` (it is a linter's regex), and inside correction narratives that quote the retired value in order to refute it — for example `research/manuscripts/aso/fusion-junction-aso-working-record.md:2772` (*"§5.1 read 'the longest shared 3′ donor run is three nucleotides.' Three is the **EWSR1** maximum. The panel-wide within-partner maximum is **five**"*) and `research/manuscripts/aso/fusion-junction-aso-paper-redteam-round7.md:156`. Those are the discipline working.

**One survives verification and is a real inverse defect.** `PRIMARY`.

Registry entry `vaccine_coverage_wilson_intervals`, `"pattern": "95% CI (?:8\\.26|26\\.6)"`:

> `"current"`: *"**withdrawn**. The intervals pooled every AFND population into a single binomial while the same records show HLA-B\*15:01 ranging from 0 to 0.4007 in frequency across those populations, so the homogeneity …"*
> `"retired_by"`: *"Round 1 of the vaccine-path hardening cycle, **2026-08-22**, statistics seat, verified against `hla_coverage.py:83-92` and `:168-197` and the `af_range_across_populations` field."*

Both retired intervals are printed as **current, unqualified figures** in `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md`, in two places:

`:58` —
> HLA class-I population coverage (AFND frequencies, IEDB formula) is **≈8.5%** … (B\*15:01 alone; 8.51%, **95% CI 8.26–8.76%**) and **≈27%** for all strong-binder alleles pooled (27.4%, **95% CI 26.6–28.1%**)

`:246-248` —
> - … covers **≈8.5% of patients** — 8.51% (**95% CI 8.26–8.76%**).
> - Pooling **all strong-binder alleles** … reaches **≈27%** — 27.4% (**95% CI 26.6–28.1%**).

Neither carries a retention marker for the intervals. Two markers *do* sit at `:60-64`, but by their own text they cover **different clauses** — the class-II arm (*"⚠ Superseded, retained (updated 2026-08-22): 'The class-II (CD4 helper) arm and the combined both-arms figure are **withdrawn pending regeneration** …'"*) and the both-arms wording (*"⚠ Superseded, retained (corrected 2026-08-28): 'the both-arms figure is not computed rather than withdrawn'."*). The intervals themselves are unmarked.

**Why nothing caught it: `fusion-junction-neoantigen-paper.md` is not in `targets[]`.** The registry lists only its sibling, `research/manuscripts/neoantigen/emc-vaccine-development-path.md`. The linter is structurally blind to the paper, and exits 0.

That is the general shape of the inverse defect in this repository: **not a missing registry entry, but a registry entry whose enforcement scope (29 files) is 0.37 % of the tracked tree (7,741 files).** The discipline is written correctly and recorded correctly; it is simply not looked for outside 29 files. `SECONDARY` for the generalisation, `PRIMARY` for the one verified instance.

I did **not** apply any correction.

### Part 4 — preregistrations: no correction was applied inside one in a way that destroys the frozen text; two disclosed in-body edits exist and I quote them

Denominator: **12 preregistration documents** (`git ls-files | grep -i -E "prereg|pre-reg"` returns 13 paths, one of which is a test file). Ten declare `status: immutable`; `nr4a-repanel-prereg-DRAFT.md` declares `status: superseded` with `superseded_by:`; `nr4a3-ternary-coop-prereg.json` carries no status field.

**Answer: no. I found no case where a correction overwrote or deleted a preregistered criterion.** The dominant pattern is correct and, where I read the frozen text, verifiably so:

- `research/modalities/nr4a3-druggability-prereg.md` — the correction lives in an appended **`## Deviation log (append-only; preserves pre-registration integrity)`** at `:89`, which discloses that Gate 0's discriminator was changed and `D* = 0.53` set. I read the frozen Gate 0 section at `:36-48` to check: it **still reads the original**, unedited — *"the occluded Nurr1 apo crystal `1OVL` scores its max **< 0.5**"* — the criterion the deviation log says fails as literally specified. Correction beside, not inside. This is the reference implementation.
- `research/modalities/nrv04-retrospective-prereg.json:91` states the rule explicitly: *"CURRENT value, post-AMENDMENT 3 defect 1 (2026-07-25). The prose §2b above it is the FROZEN 2026-07-24 text and is **deliberately left unedited**; the amendment is the dated correction."*
- `research/modalities/nr4a3-nrv04-retrospective-prereg.md:178-182` — *"⚠ **The next two lines are SUPERSEDED by AMENDMENT 4 (2026-07-31)** … Retained for the record"* — marker beside the retained frozen lines, pointing at an appended amendment.
- `research/modalities/nr4a3-nrv04-covalent-feasibility-prereg.md:25-26` — *"⚠ **AMENDED 2026-07-25** — see AMENDMENT 1 at the end of this file. **The frozen text below is left UNEDITED** so the original rule and the amendment can both be read."*

**Two in-body edits exist. I flag them, quote them, and do not overstate them.**

**(a) `research/modalities/nr4a3-nrv04-retrospective-prereg.md:271`**, inside §7 of the frozen body:

> Per-leg cost is **MEASURED** (the 18-leg covalent panel, **~$0.43/leg** … ). *(Corrected 2026-07-25 from the ~$0.45 this line carried — the final ledger mean is $0.43.)*

The line's number was changed in place. The same file's freeze note at `:324` reads:

> *Frozen 2026-07-24, before any retrospective leg ran. **Amendments must be dated additions to this file, never silent edits to a criterion.***

Assessed against that wording: the edit is **dated**, **not silent** (it retains `~$0.45` and says when and why), and `~$0.43/leg` is a **measured cost figure, not a criterion**. So it is inside a preregistration, but it is not the defect class the freeze note forbids. I record it as the closest case found and leave the judgement to the owner.

**(b) `research/modalities/emc-atri-prereg.md:34`**, in the opening blockquote of a `status: immutable` file:

> ⚠ **Superseded, retained (2026-08-03):** an earlier framing of this file, and of route 1 in the options memo, described the panel as *"the cheapest wet-lab ask"* … The corrected reading: route 1's ask is **the least demanding of the wet-lab-gated routes** …

This corrects the file's own **framing**, retains the superseded wording verbatim, and is dated — but it sits in the document body rather than as a dated appended amendment, and it is not a criterion. Same assessment: disclosed, retained, dated, non-criterion.

**No preregistration in this tree has had a hypothesis, endpoint, alpha, direction, gate predicate, or unit of independence rewritten in place.** Where those changed, they changed by numbered dated amendment with the frozen text left standing — `nrv04-retrospective-prereg.json:10` records AMENDMENT 4 explicitly as *"panel 18 -> 16 legs … **No gate predicate, endpoint, alpha, direction or unit of independence changed**."*

## Validation evidence

**RUN**

| # | command (cwd `/home/user/Rare-cancers` unless noted) | exit | key output |
|---|---|---|---|
| 1 | `date -u; git rev-parse HEAD; git status --porcelain; env \| grep -i -E 'claude\|anthropic\|model' \| sed -E …` | 0 | quoted in §Worker |
| 2 | `grep -rc -i -E "supersed" --binary-files=without-match --exclude-dir=.git .` | 0 | 10,106 lines; top file 2,617 |
| 3 | `grep -o -i -E '"[a-z_0-9]*supersed[a-z_0-9]*"' research/modalities/nr4a3-orientation-basins.json …` | 0 | 924/576/576/348/286 JSON key hits — confirms the inflation |
| 4 | `python3 /tmp/claude-0/w28/scan.py` | 0 | `markers(same-line supersede+retain): 1479` / `files: 464` |
| 5 | `python3 /tmp/claude-0/w28/classify2.py` | 0 | `q2 1449/1479 (98.0%)` `r2 1106/1479 (74.8%)` `d2 986/1479 (66.7%)` |
| 6 | inline heredoc dumping ±3-line context for 20 seeded-random markers | 0 | hand-read; 20/20 carried a replacement |
| 7 | `grep -n -E "def main\|argparse\|open\(.*[\"']w\|\.write_text\|--write" research/manuscripts/lint_consistency.py` | 0 | only `--json`, `--repo`; **no write site** |
| 8 | `timeout 900 python3 research/manuscripts/lint_consistency.py` | **0** | `lint_consistency: 0 ERROR across 29 target file(s)` |
| 9 | `timeout 600 python3 /tmp/claude-0/w28/pin.py` | 0 | `artifact_missing 0  key_missing 0  doc_missing 0  value_absent 2  ok 97` |
| 10 | `grep -n -E "4\.568\|2\.538\|4\.57\|2\.54" research/manuscripts/dependency/emc-biomarker-selected-classes.md` | 0 | `:194  … (*t* = −4.57 and −2.54)` → both agree, U+2212 |
| 11 | `timeout 300 python3 -` (superseded-pattern reachability over the 29 targets) | 0 | `81 entries, 0 bad regex, 23 match nowhere in targets` |
| 12 | `timeout 400 python3 -` (23 patterns × 6,927 non-target tracked files) | 0 | per-pattern hit/unmarked table quoted in Part 3 |
| 13 | `git ls-files \| grep -i -E "prereg\|pre-reg"` | 0 | 13 paths (12 documents + 1 test) |
| 14 | per-prereg `grep -n -i -E "supersed\|retained\|amend\|corrected\|immutable\|revis"` + `git log --oneline --follow` | 0 | every prereg: **1 commit** |
| 15 | `git rev-list --count HEAD`; `git log --format='%h %ad' --date=short \| tail -3`; `git ls-files \| wc -l` | 0 | `340`; oldest `2026-09-04`; `7741` |
| 16 | inline heredoc: `git log --follow` over all 29 `targets[]` | 0 | `total commit-touches: 31` |
| 17 | `sed -n` reads of `nr4a3-druggability-prereg.md:36-53,80-105`, `nr4a3-nrv04-retrospective-prereg.md:260-290,318-332`, `emc-atri-prereg.md:1-46`, `fusion-junction-neoantigen-paper.md:54-75,243-250` | 0 | quoted verbatim above |
| 18 | `git log --oneline 98a0833f..HEAD; git diff --name-only 98a0833f..HEAD; date -u; git rev-parse HEAD; git status --porcelain` | 0 | 7 commits, 32 files, **all campaign reports**; nothing I measured changed |

One background job (`bh5m26ymp`, the first tree-wide `superseded[]` reachability scan) exceeded its 120 s foreground window and produced **no output file**; I did not use it and replaced it with the bounded runs #11 and #12. Recording it so the count is honest.

**PROPOSED (NOT RUN)**

- Extending `targets[]` to cover the manuscripts that quote registry-pinned quantities — at minimum `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md` — and re-running `lint_consistency.py` to see the true error count. **NOT RUN**: adding a target is a write to `pinned-figures.json`, outside my write isolation, and it may surface further errors that only the file owner should adjudicate.
- Tightening `valb_rung_band_8_78_22_28`'s bare-number pattern to a multi-token form per the registry's own `_README`. **NOT RUN**: same reason.
- `scripts/preflight.sh` / `PREFLIGHT_FULL=1`. **NOT RUN**: forbidden by dispatch.
- Any repair to `publications.json:305` per W09f R.3. **NOT RUN**: not my lane, and I was told not to apply corrections.

## Limitations

- **The date/commit screen is a screen.** It looks for `\b20\d\d-\d\d-\d\d\b` or a 7–40-char hex token within ±4 lines. It will miss a date written as "August 15" or "last Tuesday", and the hex pattern can false-positive on hashes that are not commit references — so the true rate of date-less markers may be either side of 33.3 %. The eight hand-verified examples are solid; the aggregate is approximate.
- **JSON records defeat line-based context.** `routes.json`, `publications.json` and `research-ledger.json` put an entire record on one physical line, so "within ±4 lines" is meaningless there — a date anywhere in a 4,000-character record counts as adjacent. This inflates `d2` for JSON files, i.e. the real date-coverage figure is likely **worse** than 66.7 %.
- **Part 3 is under-powered and I cannot fix that here.** With no pre-2026-09-04 file history, I cannot enumerate value changes; I can only detect old values that still sit in current prose. A value that changed cleanly with no retention marker and left no trace is **UNKNOWN** and undetectable from this checkout.
- **Marker recall.** I required `supersed*` and `retain*` on the *same line*. A marker that puts "Superseded" on one line and "retained" on the next is missed. `WAVE-LOG.md:102`-style prose retention with neither token adjacent is missed entirely. 1,479 is a floor, not a census.
- **I did not read the frozen corpus** at `/tmp/claude-0/frozen-corpus/`. Where I say something is absent from the tree, that is absent from the live checkout at `98a0833f`, and per COMMON-BRIEF §2 absence is **UNKNOWN**, not proof.
- **No clinical claim.** Nothing here touches EMC efficacy, safety, selectivity or readiness; the neoantigen finding is about a *statistical interval's* provenance in a manuscript, not about whether any vaccine works. There is no wet lab.
- I read `lint_consistency.py` for write sites before running it, but I did not audit its 648 lines for correctness. Its `0 ERROR` is evidence that **its own rules** pass, not that the rules are sufficient — indeed Part 3's finding is precisely that they are not, for scope reasons.

## Stop condition

**Set up front:** return as soon as all four parts have (i) a stated honest denominator and (ii) either an enumerated defect list with file:line or a plainly stated clean result — or a recorded reason the part is not executable.

**Met.** Part 1: denominator 1,479/464, defect class enumerated with hand-verified file:line examples. Part 2: denominator 183 entries + 29 targets, **clean**, independently re-derived rather than taken from the linter. Part 3: prescribed method recorded as **not executable** with the evidence (`31 commit-touches across 29 files`, 340 commits from 2026-09-04), substitute method run, one verified instance returned. Part 4: **no**, with the two closest cases quoted. Not blocked; no content-policy refusal was encountered on any branch.

## Tool-call and wall-clock count actually used

**32 tool calls** (31 `Bash`, 1 `Read` of a persisted tool-result file). **Wall clock 03:13:48 → 03:23:22 UTC = 9 min 34 s** of tool execution, under the ~40-call / ~40-minute target. One background job started and discarded unused (counted in the 32).

## Next concrete action

**One specific successor task, for the owner of `research/manuscripts/pinned-figures.json`:** decide whether `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md` should be added to `targets[]`, then re-run `python3 research/manuscripts/lint_consistency.py` and adjudicate the errors it raises — starting with the two live printings of the withdrawn Wilson intervals at `:58` and `:246-248`, which entry `vaccine_coverage_wilson_intervals` records as retired on 2026-08-22 by the statistics seat for invalid single-binomial pooling across AFND populations. That is a single-file scope change with a single verification command, and it converts the one confirmed inverse defect into either a repair or a recorded decision. It is a **submission-blocker class** finding for the vaccine-path manuscript (a current statistic the repository's own registry says is withdrawn), not maintenance — but the repair is the paper owner's to make, not mine.
