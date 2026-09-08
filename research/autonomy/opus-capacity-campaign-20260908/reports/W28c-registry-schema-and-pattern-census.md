<!-- collected 2026-09-08T03:49:31Z by campaign coordinator; agent id a18183c2f5558358a; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a18183c2f5558358a.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

## Worker

**W28c**, lane: superseded-guard liveness — registry-wide (named successor to W28b), OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model — `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the served model from the transcript.

**Write isolation honoured.** Nothing written under `/home/user/Rare-cancers`; no git write operation; no registry edit, no pattern repair, no field added, no entry moved. All execution under `/tmp/claude-0/w28c/`, deleted before returning (`scratch deleted`). `scripts/preflight.sh` not run. No network, no paid API, no GPU spend. `atr_hrd_sarcoma_series.py` never invoked.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:40:33 UTC 2026` | `Tue Sep  8 03:45:59 UTC 2026` |
| `git rev-parse HEAD` | `5ae0fa04ff9516ac8f820381079d644a094f4a77` | `606d79f96526b651f3b825190d721f6b302c032e` |
| `git status --porcelain` | empty | empty |

HEAD moved once (coordinator collecting reports). `git diff --name-only 5ae0fa04..606d79f9 | grep -v opus-capacity-campaign` returns **nothing**, and `git diff --stat 5ae0fa04..606d79f9 -- research/manuscripts/pinned-figures.json research/manuscripts/lint_consistency.py STRATEGY.md` is **empty** — every file I measured is byte-identical across the move. Not the frozen `92abbcb` (per the corrected brief, there is no pin).

Literal `env` output, model-relevant lines (proxy lists elided as marked, nothing else removed):

```
AI_AGENT=claude-code_2-1-263_agent
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDECODE=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_EFFORT=medium
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
SESSION_INGRESS_URL=https://api.anthropic.com
no_proxy=…  [elided]   GLOBAL_AGENT_NO_PROXY=…  [elided]   NO_PROXY=…  [elided]
npm_config_noproxy=…  [elided]   JAVA_TOOL_OPTIONS=…  [elided, proxy/truststore]
```
No variable names a served model.

## Question

Three, all registry-wide rather than confined to W28b's six dead guards:

1. **Schema completeness** across all 81 `superseded[]` entries and every other list in `pinned-figures.json` — which entries would crash `lint_consistency.py`'s finding formatter if they fired, and which carry fields no code reads.
2. **Pattern-shape fragility across all 81** — for each entry, would its pattern still match the retired value *written as the entry's own `current`/`note` field writes that quantity*? WOULD-MATCH / WOULD-NOT-MATCH / UNTESTABLE-from-the-registry.
3. **Verify or refute W28b's `$126.17` observation** — that the registry carries one figure as both a current best estimate (two entries) and a retired one (a third), with `STRATEGY.md:128` stating it as current.

Open because W28b tested six of 81 and explicitly declined to generalise ("I stopped there and did not open the registry-wide schema audit those suggest").

## Prior-work check

Read in full: `CLAUDE.md`, `COMMON-BRIEF.md` (including the 03:36Z correction and the "Known, measured, and NOT worth rediscovering" section), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W28b-dead-guard-fixture-check.md`, and the head of `reports/W28-superseded-marker-audit.md` through Part 1. W25 not read, not referenced.

`CLOSED-WORK.md` closes nothing in this lane — it covers scientific gates (Davis, Hofvander, Brenca, promoter transfer, pazopanib/sunitinib/CTARC recovery, registry ICD-O), the NR4A Perspective refusal, retained-source limits and lane-11 source-index ownership. Nothing about the pinned-figures registry.

Commands run:

- `grep -rln "pinned-figures" --include=*.py --include=*.sh --include=*.yml . | grep -v '^./.git'` → **32 files** consume the registry, not one. This is the material correction to a single-linter reading of the schema.
- `grep -rn "[\"']<field>[\"']" --include=*.py --include=*.sh --include=*.yml .` for 23 candidate field names.
- `grep -rn '"superseded"\]\|get("superseded"' --include=*.py .` → only `lint_consistency.py:601` and `test_throughput_provenance.py:163` read the list at all.
- `grep -rn "126\.17" / "133\.38" --include=*.md --include=*.json .`, excluding `.git` and the campaign directory.
- Per the brief, campaign reports are not repository evidence; I take W28b's six-guard results as premise and test the disjoint registry-wide question.

I did **not** read the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/`. Every finding is from the live checkout at the two HEADs above, and the two files I analysed are identical across them.

## Method / inputs

Files read at HEAD: `research/manuscripts/pinned-figures.json` (2,050 lines), `research/manuscripts/lint_consistency.py` (648 lines), `research/modalities/tests/test_lint_consistency.py`, `systems/parser_guard.py:110-150`, `research/manuscripts/claim_audit.py:485-500`, `research/manuscripts/claim_coverage.py:490-520`, `research/manuscripts/tests/test_pinned_figures_every_home.py`, `test_pin_remediations_name_the_generator_that_writes_the_artifact.py`, `test_throughput_provenance.py:150-166`, `STRATEGY.md:124-132`, `research/modalities/realised-spend.json`.

Tools: `python3 3.11.15` stdlib (`json`, `re`, `importlib`), `git`, `grep`. Four scratch scripts under `/tmp/claude-0/w28c/` — `frame.py`, `liveprobe.py`, `classify.py`, `transplant.py` — all deleted; their decisive source and output are quoted below.

**Fixture rule, inherited from W28b and binding here.** A fixture is admissible only if its wording comes from committed text. My admissible source is the **transplant fixture**: the entry's own `current` sentence with its *current* numerals replaced by the *retired* numerals the pattern hard-codes. Nothing else is invented. **I never unescaped a pattern into a string and called the match a pass** — that proves only that the regex parses.

## Result

### R.1 — Schema completeness: the crash pair is exactly 2, and it is confined to `superseded[]` `PRIMARY`

Field census over all 81 `superseded[]` entries and all four other lists, `RUN`:

| list | n | required-by-code fields all present? |
|---|---|---|
| `derivations` | 1 | yes |
| `artifact_figures` | 99 | yes (`id`/`artifact`/`key`/`context`/`must_appear_in` 99/99) |
| `table_completeness` | 1 | yes |
| `subset_checks` | 1 | yes |
| `superseded` | 81 | **no — `current` 80/81, `retired_by` 79/81** |

**W28b's crash pair is confirmed and is the complete set.** `check_superseded` (`lint_consistency.py:610-612`) is the only formatter in the file using direct `dict` subscripts on fields that are not universally present; every other check reaches its optional fields through `.get()`. Missing `current`: `aso_thermo_cross_margin_discordance`. Missing `retired_by`: `realised_spend_omitted_the_selcal_lane`, `aso_thermo_cross_margin_discordance`. No other list can raise `KeyError` in a finding path. `id`/`pattern` are 81/81; no duplicate `id` in `superseded[]` or `artifact_figures[]`; all 29 `targets[]` paths exist.

### R.2 — Dead fields: eleven, in every list, and `must_not_appear_in` is carried by four entries, not one `PRIMARY`

W28b reported `must_not_appear_in` as dead metadata on **one** entry. Dead: confirmed. **One entry: refuted — it is four.**

| field | list | carriers | read by any of the 32 consumers? |
|---|---|---|---|
| `must_not_appear_in` | `superseded` | **4** — `vaccine_e7_coverage_stated_without_a_panel`, `vaccine_coverage_ceiling`, `vaccine_combined_cd8_cd4_is_null`, `vaccine_coverage_wilson_intervals` | **no** |
| `why_pattern_widened` | `superseded` | 3 | no |
| `scoping_note` | `superseded` | 2 | no |
| `_widened_2026_08_02` | `superseded` | 1 | no |
| `_narrowed_2026_07_30` | `superseded` | 1 | no |
| `artifact` | `superseded` | 1 | no (`artifact` **is** read in `artifact_figures[]`; the `superseded[]` copy is not) |
| `note` | `superseded` | 1 | no |
| `id_note` | `superseded` | 1 | no |
| `description` | `derivations` (1), `artifact_figures` (99), `table_completeness` (1) | 101 | **no** — read only for `subset_checks` (`lint_consistency.py:586`) |
| `_context_history` / `_context_note` | `artifact_figures` | 3 / 1 | no |
| `_non_tool_note` / `_must_appear_in_note` | `derivations` | 1 / 1 | no |

Two consequences worth separating from the raw count.

⛔ **All four `must_not_appear_in` values name `research/manuscripts/neoantigen/emc-vaccine-development-path.md`, which is in `targets[]`.** So the field declares a scope *narrower* than the one actually executed: those four patterns are run against all 29 targets while the entry says one file. That is not a lint failure today — the declared file is a subset of the executed set — but the field reads as a scope restriction and is not one.

⛔ **`parser_guard.check_paths` validates `must_appear_in`/`file` paths for `derivations`, `artifact_figures`, `table_completeness` and `subset_checks` (`parser_guard.py:132`) and skips `superseded` entirely.** So a `must_not_appear_in` path that is renamed or deleted is caught by nothing, in a repository that already guards the same failure for every other list.

⚠ The `_`-prefixed fields are self-evidently documentary by convention. `description` (101 carriers), `must_not_appear_in`, `why_pattern_widened`, `scoping_note`, `id_note`, and `superseded[].artifact`/`note` are not prefixed and read as machine fields.

### R.3 — Pattern-shape fragility across all 81 `PRIMARY`

Method, reproducible. For each of the 81, split the pattern on top-level `|` (respecting `\|`, `(...)` and `[...]`; W28b's naive split produced spurious `bad escape` lines — my splitter reproduces its Run-2 hand-split for the vaccine guard). For each alternative build the **frame** by wildcarding numeric literals, then search the frame against the entry's own `current`. A frame hit means the entry's own current field writes the quantity in a sentence shape the pattern accepts, so the retired value in that shape would fire.

| verdict | n | meaning |
|---|---|---|
| **WOULD-MATCH** | **40** | ≥1 alternative's frame matches the entry's own `current` |
| **WOULD-NOT-MATCH** | **13** | transplant fixture admissible from the entry's own `current`; **every** alternative fails it |
| **UNTESTABLE-from-the-registry** | **28** | no admissible fixture: `current` absent, bare-valued, or written in vocabulary that abandons the retired sentence |

The 13 WOULD-NOT-MATCH, each with its transplant fixture and the construct that defeats it — all verified by a real run against the compiled registry patterns:

| entry | transplant fixture (its own `current`, retired numerals) | what breaks |
|---|---|---|
| `realised_spend_before_orphan_leak` | `Attested-only is $2.31 and the best estimate $79.59, both DERIVED from …` | needs `+$2.31 attested`; and `best estimate **is** **$79.59**` |
| `realised_spend_before_retro_orphan_leak` | `Attested-only is $22.31 and the best estimate $99.59, both DERIVED from …` | same two |
| `commit_loop_gate13_39s_55_tests` | `gate 13 is 39.3 s over 55 tests (2026-08-24)` | pattern wants `gate 13 **39.3 s**` — bold, **no** copula; current writes `is`, no bold |
| `commit_loop_about_75_seconds` | `the DEFAULT commit loop is 75.0 s — about one minute` | pattern wants `about 75 seconds`; the field's unit convention is `s` |
| `commit_loop_about_nine_minutes` | `the DEFAULT commit loop is 540 s — about nine minutes` | `about **9** min` / `ABOUT NINE ON A QUIET BOX` — neither shape survives |
| `commit_loop_citation_provenance_44s` | `gate 6 (citation provenance and publication type) is 44.4 s` | pattern wants `citation provenance is 44.4 s`; four words intervene |
| `aso_canonical_file_condemned_record_count_250` | `250 records reach the ten-base-pair criterion` | pattern wants `250 records in the file` |
| `aso_canonical_file_junction_key_count_40` | `The file keys a row to 40 distinct junctions` | pattern locks the **inverted** clause order `of the 40 junctions this file keys a row to` |
| `aso_within_partner_shared_donor_run_three_nt` | `three nucleotides — the panel-wide within-partner maximum` | pattern wants `longest shared 3' donor run is three` |
| `thiol_hg_occlusion_first_gen` | `median 0.76 (76 %) of the SG surface occluded by the residue's own HG proton` | pattern wants `median 76 %` adjacent; the field writes fraction-first, percent in parentheses |
| `xtt_pre_harmonized` | `4/20 detected, 3 ≥ D*` | pattern wants `4/20 above` or `4/20 conformers` |
| `buy_line_1_5x_multiple_expression` | `$0.006539/ns (≈1.5x the current basis)` | pattern hard-codes `1.5x the **ladder** basis`; the field writes `current basis` |
| `card_ratio_4090_over_4080_within_7pct` | `RTX 4090 / RTX 4080 = 1.070x … (the 4080 is ~7% behind)` | pattern wants `the 4080 is **within** 7 %`; the field writes `behind` |

⛔ **W28b's "one author's habit across three guards" is confirmed and extended to a repository-wide construct class.** The failure is never the number and never the regex's validity: it is a **fixed function word or a fixed emphasis position** — a required `is` (three entries), a forbidden `is` (`gate 13 **39.3 s**`), asterisks hugging the figure (four entries), a locked clause order (two), a fixed adjective (`ladder` vs `current`, `within` vs `behind`), a fixed unit spelling (`seconds` vs `s`). Thirteen of 81 (16%) fail the only fixture the registry itself licenses.

⚠ **One correction to my own screen, and it is why the transplant run matters.** My frame screen initially placed `rbfe_edge_tyk2_rate` in WOULD-NOT-MATCH. The transplant run refuted it: alternative 2 (`\$0\.6[–-]1\.4`) fires on the fixture. I moved it to WOULD-MATCH. 1 of 14 screened calls was wrong, and the run — not the screen — decides.

⚠ **Also correcting W28b, in its favour twice over.** W28b graded `realised_spend_before_orphan_leak` and `..._retro_orphan_leak` **UNTESTABLE** because neither entry quotes the retired sentence. Both entries' `current` fields do model the sentence for the very quantity pair the pattern guards (*"Attested-only is $48.89 and the best estimate $126.17"*), so a transplant fixture **is** admissible under the shared rule, and both fail on both alternatives. They are **WOULD-NOT-MATCH**, not UNKNOWN. W28b's caveat still governs the interpretation: a NO MATCH against the registry's own current phrasing is **not** proof the guard was born broken against text this shallow checkout (346 commits) cannot show.

⛔ **One entry's pattern matches its own `current` text verbatim** — `commit_loop_gate13_446s_85_to_94_percent`, whose `current` retains the retired readings as history: *"The 446.3 s / 1247.8 s readings described the gate BEFORE its hot spot was removed."* Alternatives `446\.3 s` and `1247\.8 s` both fire on it. `grep -rn "446\.3 s\|1247\.8 s"` over `CLAUDE.md`, `STRATEGY.md` and `CLAUDE-history.md` returns **nothing**, so this is latent, not live — but it is the same shape as W28b's `aso_thermo` control finding, arriving by content rather than by capture group: a guard whose retired literal sits inside the sentence the registry itself tells a writer to copy.

⚠ **Structural note, offered as a reading and not a defect.** 7 of 81 patterns hard-code no retired numeral at all (`aso_standard_practice_excludes_parents`, `no_ternary_leg_completed`, `no_protein_mutation_engine`, `genmatched_null_degenerate_statistics`, both `pose_singular_*`, and `aso_thermo_cross_margin_discordance`). These retire a *framing*, not a value; their `current` asserts the negation and so can never serve as a transplant fixture. **UNTESTABLE is the correct and expected verdict for that class, not a finding** — and it accounts for a good share of the 28. The odd one out is `aso_thermo_cross_margin_discordance`, whose numerals exist only inside `[0-9]` classes: it is value-shaped but value-agnostic, exactly W28b's R.1 #5. I make no filing judgement on it.

### R.4 — The `$126.17` observation: CONFIRMED, with one location refinement and one consequence that refutes the repair's expected yield `PRIMARY`

`grep -rn "126\.17"` over `*.md`/`*.json`, excluding `.git` and the campaign directory, returns exactly **three** tracked-tree statements — all of them stating it as a current best estimate:

| location | text | status |
|---|---|---|
| `pinned-figures.json:1848` | `current` of `realised_spend_before_orphan_leak`: *"Attested-only is $48.89 and the best estimate $126.17, both DERIVED …"* | current |
| `pinned-figures.json:1854` | `current` of `realised_spend_before_retro_orphan_leak`: identical opening clause | current |
| `STRATEGY.md:128` | *"Current: attested **$48.89**, best estimate **$126.17**, both DERIVED (`realised_spend.py --write`)"* | current |

Against which `realised_spend_omitted_the_selcal_lane` declares `best estimate is \*\*\$126\.17\*\*` **retired** as of 2026-08-02, its `current` reading *"realised spend is $84.49 machine-ledgered, best estimate $133.38"* — and the machine artifact agrees: `research/modalities/realised-spend.json:82` carries `"realised_usd_best_estimate": 133.38`.

**Verdict: W28b's observation is confirmed on all three counts.** One refinement it did not state: `STRATEGY.md:128` is **Appendix A row 58**, i.e. the file's superseded-numbers record, not its live Spend summary — the sentence is a current-tense claim sitting inside a retirement record.

⛔ **And that location has a consequence that partly refutes W28b's own "single highest-yield pattern repair" framing.** I probed the real linter read-only. The as-written alternative `best estimate is \*\*\$126\.17\*\*` does **not** match `STRATEGY.md:128`. The hypothetical repaired alternative with the copula dropped, `best estimate \*\*\$126\.17\*\*`, **does** match — and `lc.is_cleared(...)` returns **`True`** for it, because `lc._enclosing_heading` resolves to `## Appendix A — superseded numbers and retracted claims`, one of the section headings `is_cleared` clears wholesale.

**So repairing the `best estimate is \*\*\$…\*\*` construction would produce no new finding at the one live site the figure occupies.** The repair remains correct on its merits — 13 entries fail their own transplant fixture — but its yield against today's tree is zero, and the `$126.17` disagreement is a **content** question for the file owner (three current-tense statements of a figure a fourth entry retires, against a machine artifact that says $133.38), not something a pattern fix reaches. I record the disagreement and leave it, as W28b did.

### R.5 — The tree passes today; every defect above is latent `PRIMARY`

```
$ python3 research/manuscripts/lint_consistency.py
lint_consistency: 0 ERROR across 29 target file(s)
LINT_EXIT=0
```

## Validation evidence

All `RUN`, `python 3.11.15`, scratch under `/tmp/claude-0/w28c/` (deleted), against `/home/user/Rare-cancers`, inputs byte-identical across the HEAD move.

**Run 1 — `frame.py`, exit 0.** Field census, top-level alternation split, frame construction. Verbatim:
```
FULL PATTERNS THAT FAIL TO COMPILE: []
ALTS THAT FAIL TO COMPILE (splitting artifacts flagged): []
superseded missing current: ['aso_thermo_cross_margin_discordance']
superseded missing retired_by: ['realised_spend_omitted_the_selcal_lane', 'aso_thermo_cross_margin_discordance']
superseded missing id/pattern: []
other-list required-field scan done
superseded dup ids: []   artifact_figures dup ids: []
FRAME MATCHES current, ALL alts (24) / SOME alts (15) / NOTHING (41) / NO current FIELD (1)
entries whose OWN pattern matches their OWN current text (raw):
   commit_loop_gate13_446s_85_to_94_percent ['446\\.3 s', '1247\\.8 s']
```
81/81 patterns compile — W28b's 0-bad-regex count stands, and the top-level splitter reproduces its corrected hand-split. Two `FutureWarning: Possible nested set` lines came from my own wildcarding inside the two patterns that carry digits in a character class (`two_mechanism_grid_limit`, `aso_thermo_cross_margin_discordance`); both are hand-classified, so the warning is a harness artifact, not a registry defect.

**Run 2 — `transplant.py`, exit 0.** 14 transplant fixtures against the real compiled patterns:
```
NO MATCH  realised_spend_before_orphan_leak
NO MATCH  realised_spend_before_retro_orphan_leak
NO MATCH  commit_loop_about_75_seconds
NO MATCH  commit_loop_about_nine_minutes
NO MATCH  commit_loop_gate13_39s_55_tests
NO MATCH  commit_loop_citation_provenance_44s
NO MATCH  aso_canonical_file_condemned_record_count_250
NO MATCH  aso_canonical_file_junction_key_count_40
NO MATCH  aso_within_partner_shared_donor_run_three_nt
NO MATCH  thiol_hg_occlusion_first_gen
NO MATCH  xtt_pre_harmonized
MATCH     rbfe_edge_tyk2_rate
NO MATCH  buy_line_1_5x_multiple_expression
NO MATCH  card_ratio_4090_over_4080_within_7pct

fixtures that DID match (would refute my WOULD-NOT-MATCH call): 1 of 14
```

**Run 3 — `liveprobe.py`, exit 0.** Real `lint_consistency.py` loaded via `importlib`, read-only, against real `STRATEGY.md`:
```
line128 contains '126.17': True
  as-written: no match
  hypothetical-without-is: MATCH
   is_cleared: True
enclosing heading: ## Appendix A — superseded numbers and retracted claims
```

**Run 4 — the real linter, unmodified:** `lint_consistency: 0 ERROR across 29 target file(s)`, `LINT_EXIT=0`.

**Run 5 — consumer census.** `grep -rln "pinned-figures" --include=*.py --include=*.sh --include=*.yml` → 32 files; per-field `grep` over all of them for 23 field names, yielding R.2's table.

**`PROPOSED (NOT RUN)`** — everything in "Next concrete action". No repair, test, registry edit, field addition, pattern change or `targets[]` change was written or executed. `PREFLIGHT_FULL` and `scripts/preflight.sh` not run.

## Limitations

- **A WOULD-NOT-MATCH verdict is about the registry's own current phrasing, not about the original retired line.** The clone is shallow (346 commits) and pre-window wording is unrecoverable, so none of the 13 is graded "born broken". That is an unrecovered source, not an absence.
- **UNTESTABLE is 28 of 81 and is not a defect count.** At least 7 are claim-shape guards for which no fixture can exist by construction; the rest have `current` fields that are bare values, deletions ("DELETED, not replaced", "withdrawn", "NOT COMPUTED") or prose in changed vocabulary. Reporting them as broken would be exactly the circularity the fixture rule forbids.
- **My frame screen has a measured error rate: 1 of 14 screened calls was wrong** (`rbfe_edge_tyk2_rate`), caught only by the transplant run. The 40 WOULD-MATCH are screen results confirmed for the frame, not individually transplant-tested; a strict re-run should transplant all 40.
- I tested **regex liveness only**. I did not test `is_cleared` behaviour beyond the single `STRATEGY.md:128` probe, and I did not test whether any WOULD-MATCH guard would be spuriously cleared elsewhere.
- **Left with the file owner, untouched, as W28b left them:** whether `aso_thermo_cross_margin_discordance` is misfiled; whether `fusion-junction-neoantigen-paper.md` belongs in `targets[]`; and the `$126.17` current-vs-retired content disagreement of R.4.
- Nothing here is a scientific or clinical claim. It concerns a lint registry. There is no wet lab and no patient-facing consequence.

## Stop condition

Set up front: **stop when (a) every list in `pinned-figures.json` has a required-field completeness verdict and a dead-field list, (b) all 81 `superseded[]` entries carry a WOULD-MATCH / WOULD-NOT-MATCH / UNTESTABLE verdict under the fixture rule, and (c) the `$126.17` observation is confirmed or refuted against committed text — with a real `lint_consistency.py` exit code recorded.**

**MET.** (a) R.1 + R.2 — 5 lists, 2 crash entries, 11 dead fields. (b) R.3 — 81 verdicts, 40/13/28, with all 13 negatives evidenced by a run. (c) R.4 — confirmed, with the Appendix-A location refinement and the `is_cleared` consequence. Exit code recorded in R.5. Stopped there.

## Tool-call and wall-clock count actually used

**24 tool calls** (all `Bash`), against a ~40 target. **Wall clock 03:40:33Z → 03:45:59Z = 5 min 26 s**, against a ~40 min target. Under both: the whole registry is one `json` load, and the decisive evidence was three scripts and one grep census.

## Next concrete action

**For the owner of `pinned-figures.json`, one bounded change with one verification command, unchanged from W28b's and now measured against the whole registry rather than six entries:** add `retired_by` to `realised_spend_omitted_the_selcal_lane` and `current` + `retired_by` to `aso_thermo_cross_margin_discordance`, then re-run `python3 research/manuscripts/lint_consistency.py`. R.1 establishes these are **the complete** crash set across all 183 registry entries in all five lists — 2 of 81, 0 of the other 102 — so the change is bounded by measurement, not by hope, and needs no judgement about any manuscript's prose.

Three things that should travel with it but are **not** part of that action:

1. **The pattern-shape repair is worth doing and its yield against today's tree is zero.** 13 of 81 fail their own transplant fixture on a function word or an emphasis position (R.3), but the only live site of the flagship case is already cleared by `Appendix A` heading scope (R.4). Repair it for the next reintroduction, not for a finding today.
2. **`must_not_appear_in` is dead on four entries and `parser_guard` skips `superseded[]` path validation** (R.2) — a gap the same guard already closes for every other list.
3. **`$126.17` stands as a current best estimate in three tracked-tree places against a machine artifact reading `$133.38`** (R.4). That is a content question, and I left it with its owner.

**One successor task for this lane, if it is wanted:** transplant-test the 40 WOULD-MATCH entries individually rather than by frame screen, since the screen's measured error rate on this registry is 1 in 14. **No successor is needed for the UNTESTABLE 28** — the registry cannot license a fixture for them, and W28's own `X-pattern-found-nothing` precedent (its R.3) is the mechanism that would settle them, which is a code change and therefore not this lane's to author.
