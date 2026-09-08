<!-- collected 2026-09-08T04:43:16Z by campaign coordinator; agent id a81b6a18533abbc42; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a81b6a18533abbc42.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

## Worker

**W28d**, lane: superseded-guard liveness — individual transplant verification of W28c's 40 WOULD-MATCH. Campaign OPUS-CAPACITY-CAMPAIGN-20260908, successor to W28c. (Re-dispatch; the prior attempt produced no report.)

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model — `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the served model from the transcript.

**Write isolation honoured.** Nothing written under `/home/user/Rare-cancers`; no git write operation; no registry edit, no pattern repair, no field added, no entry moved between lists; no repair, patch, gate or test authored or proposed as code. All execution under `/tmp/claude-0/w28d/`, **deleted before returning** (`ls` → `No such file or directory`). `scripts/preflight.sh` not run. No network, no paid API, no GPU. W25 not read or referenced.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 04:35:15 UTC 2026` | `Tue Sep  8 04:39:56 UTC 2026` |
| `git rev-parse HEAD` | `408b676aec3625a36917755662516232a27a1278` | `408b676aec3625a36917755662516232a27a1278` |
| `git status --porcelain` | empty | empty |

**HEAD did not move this run.** I verified — not assumed — that the two files I measure are unchanged: `git diff --stat 408b676..HEAD -- research/manuscripts/pinned-figures.json research/manuscripts/lint_consistency.py` is **empty**; last commit touching either is `14a3f172d6b494d872f6d2678c7d0caa7ef26ccc`; md5 `771670eddf9633320766f017cf3bce73` (registry) and `a583a33eccc3925caefdd043503b6c66` (linter). Not the campaign's start commit `92abbcb` (per the corrected brief there is no pin).

Literal `env` output (command as prescribed; proxy/`JAVA_TOOL_OPTIONS` lines dropped by an added `grep -v -i proxy`, nothing else removed, sorted):

```
AI_AGENT=claude-code_2-1-263_agent
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDECODE=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_CHILD_SESSION=1
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_CODE_DEBUG=true
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_SYNC_SESSION_REFS=1
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_EFFORT=medium
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_PID=522
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
SESSION_INGRESS_URL=https://api.anthropic.com
```
No variable names a served model.

## Question

W28c graded all 81 `superseded[]` entries 40 WOULD-MATCH / 13 WOULD-NOT-MATCH / 28 UNTESTABLE, but the 40 rest on a **frame screen**, and W28c measured that screen wrong on **1 of 14** calls it transplant-tested (`rbfe_edge_tyk2_rate`). **Do the 40 WOULD-MATCH survive individual transplant testing, and what is the screen's measured error rate over the full 40?** Open because W28c named it its own successor task and stated the limitation explicitly ("The 40 WOULD-MATCH are screen results confirmed for the frame, not individually transplant-tested; a strict re-run should transplant all 40").

## Prior-work check

Read in full: `CLAUDE.md`, `COMMON-BRIEF.md` (including the 03:36Z HEAD correction and the whole "Known, measured, and NOT worth rediscovering" section), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W28c-registry-schema-and-pattern-census.md`, `reports/W28b-dead-guard-fixture-check.md`.

Report paths in the dispatch (`reports/W28c-…`) do not exist at the repository root; the reports live at `research/autonomy/opus-capacity-campaign-20260908/reports/`. Located by `find . -name 'W28*' -not -path './.git/*'`.

`CLOSED-WORK.md` closes nothing in this lane (scientific gates, the NR4A Perspective refusal, retained-source limits, lane-11 source-index ownership). Per the brief, sibling campaign reports are not repository evidence: I take W28c's classification as the *object under test*, not as prior art, and I re-derived the screen independently rather than trusting its list. I did **not** re-test the 28 UNTESTABLE entries. I did **not** touch the three items left with the file owner (`aso_thermo` filing, `targets[]`, the `$126.17` current-vs-retired disagreement).

Additional commands: `grep -rn "1070\.44\|793\.79\|482\.34\|481\.78\|387\.78\|242\.20" --include=*.md --include=*.json --include=*.py .` (excluding `.git` and the campaign directory) — used to look for an admissible external fixture for one entry; `grep -rn "MEASURED_NS_PER_DAY"`.

I did **not** read the frozen corpus. Every finding is from the live checkout at `408b676a`.

## Method / inputs

Files read: `research/manuscripts/pinned-figures.json` (81 `superseded[]` entries, 29 `targets[]`), `research/manuscripts/lint_consistency.py` (`check_superseded` at `:595-615`, `is_cleared`, `_read_lines`).

Tools: `python3` stdlib (`json`, `re`, `difflib`, `importlib`), `git`, `grep`. Four scratch scripts under `/tmp/claude-0/w28d/` — `transplant_all.py`, `rigor.py`, `fix.py`, `live.py` — all deleted; decisive source and output quoted below.

**Fixture rule, inherited and binding.** A fixture is admissible only if its wording comes from committed text — the entry's own field, or a verbatim quotation elsewhere in the tree. **I never unescaped a pattern into a string and called the match a pass.**

**Transplant construction, made mechanical.** For each entry: split the pattern on **top-level** `|` (respecting `\|`, `(...)`, `[...]`); for each alternative identify hard-coded numeric literals *outside* character classes and `{m,n}` quantifiers; build the frame by wildcarding those literals with capture groups; search the frame against the entry's own `current`; on a hit, rebuild `current` with the matched numerals replaced by the retired literals. That fixture is then run against the **real full compiled pattern**, exactly as `check_superseded` compiles it.

**Two rigor gates I added beyond W28c's method**, both necessary and both productive:
1. **Does the guard already fire on the *unchanged* `current`?** If so the MATCH proves nothing about the transplant.
2. **Does the match span overlap a transplanted numeral?** (via `difflib` opcodes). If not, the fixture's swap was irrelevant to the match.

## Result

### R.1 — Screen reproduction: my independent frame screen yields 39, not 40, and the difference is exactly W28c's own known error `PRIMARY`

| | n |
|---|---|
| frame-hit (my screen) | **39** |
| no frame-hit / no `current` | **42** |

My 39 are exactly W28c's 40 minus `rbfe_edge_tyk2_rate` — the one entry W28c's screen put in WOULD-NOT-MATCH and its transplant run then promoted. My 42 excluded = W28c's 13 confirmed negatives (all present in my excluded set, checked by name) + its 28 UNTESTABLE + `rbfe`. **The screen is reproducible**; two independent implementations agree entry-for-entry, and the single disagreement is the error W28c already found and corrected. I transplant-tested `rbfe` separately to complete the 40.

### R.2 — All 40 transplant-tested individually: **39 MATCH, 1 reclassified UNTESTABLE, 0 refuted** `PRIMARY`

| verdict | n |
|---|---|
| **MATCH** (transplant fires the real compiled pattern) | **39 / 40** |
| **reclassified UNTESTABLE** (no admissible fixture) | **1 / 40** |
| **NO MATCH** (screen refuted) | **0 / 40** |

**Screen error rate on the WOULD-MATCH calls: 1 of 40 (2.5%), and it is an over-inclusion, not a false positive about liveness.** No entry the screen called WOULD-MATCH turned out to be inert. Combined with W28c's `rbfe` case, the instrument's **one measured error across the whole registry is a false *negative***, not a false positive — the screen is conservative in the direction that matters least for a liveness claim. That is a materially better instrument than the 1-in-14 anecdote implied.

**The 39 MATCH, with fixtures.** 31 fixtures were built purely mechanically; 7 required hand correction (R.3); `rbfe` was built by hand. Every fixture is the entry's own `current` with only the quantity numerals swapped for the pattern's retired literals.

| entry | transplant fixture | pattern matched |
|---|---|---|
| `ladder_total_390` | `~$390 mid (~$51–614)` | `~$390` |
| `ladder_total_240` | `~$240 mid (~$51–614)` | `$240 mid` |
| `ladder_total_467` | `~$467 mid (~$51–614)` | `$467` |
| `ladder_total_128` | `~$128 mid (~$51–614)` | `$128` |
| `ladder_total_194` | `~$194 mid (~$51–614)` | `$194` |
| `ladder_total_169` | `~$169 mid (~$47–614)` | `$169 mid (~$47` |
| `ladder_total_185` | `~$185 mid (~$44–578)` | `~$185` |
| `ladder_total_158_two_leg_5aks` | `PINNED TOTAL ~$158 mid-range (~$46-626), regenerated after RUNG 5a-KS went from 2 ternary legs to 4 …` | `~$158 mid` |
| `ladder_high_band_544` | `~$46–544` | `$46–544` |
| `ternary_edge_7_15` | `~$8.8 ($7–15) per ternary edge` | `$7–15` |
| `ternary_edge_65_110` | `~$8.8 ($65–110) per ternary edge` | `$65–110` |
| `fanout_12_26` | `~$36 ($12–26) for the 19-edge fan-out` | `$12–26` |
| `fanout_91_101` | `~$36 ($91–101) for the 19-edge fan-out` | `$91–101` |
| `endpoint_leg_0_26` | `~1.38 ref GPU-h ≈ ~$0.45 per endpoint-MD leg` | `~$0.45` |
| `triangle_n1_59` | `~$5.9 (n=1 closure scout)` | `$5.9` |
| `triangle_n3_176` | `~$17.6 (n=3, 16 legs)` | `$17.6` |
| `bid_strategy_tool_total_166` | `~$166 ($35–483) for the stages the cost model prices` | `~$166` |
| `card_ratio_242` | `2.42× (4090/3090, validated grid) — and the card is not the decision, the OFFER is` | `2.42×` |
| `card_ratio_4090_over_3090_2_10` | `RTX 4090 / RTX 3090 = 2.10x on the median-of-N estimator` | `2.10x` |
| `bid_multiple` | `bid = the market floor plus a staleness tick (min_bid × 1.9, min +$0.0005), capped at on-demand` | `min_bid × 1.9` |
| `y29f_single_replicate` | `Y29F = −0.55 ± 0.175 at full 3 × 3 replication` | `−0.55` |
| `y29a_partial_replication` | `Y29A = +4.025 ± 1.077 at full 3 × 3 replication` | `4.025 ±` |
| `nrv04_a1_wrong_cysteine_899_1639` | `8.99–16.39 Å at the preregistered C551, across every clean co-fold model in the bucket` | `8.99–16.39` |
| `s1f_shakeout_offer_quote_1p41x` | `$0.00612/ns · 1.48× basis on 46000463 — the BILLED rate …` | `$0.00612/ns` |
| `ternary_lane_valb_cohort3_rates` | `valB_mini cohort 4, rented 4:51 PM ET: 1.528x / 1.500x / 1.859x / 1.649x basis (…)` | `1.528x` |
| `tier2_term_a_seven_basins` | `Tier 2 term (a) = 3 basins (…); reach fractions 0.019-0.057; conserved-cysteine control zero in 184 of 192 basins …` | `0.019-0.057` |
| `marginal_axis_resolvable_1p12_assumed_sd` | `best-case resolvable difference 1.12 kcal/mol = minimum_detectable_difference(0.375, 3) …` | `best-case resolvable difference 1.12` |
| `nrv04_retro_panel_18_of_18` | `… the primary reference distribution C(9,3)=84, and the minimum attainable one-sided p 1/56 = 0.0179 …` | `C(9,3)=84` |
| `realised_spend_omitted_the_selcal_lane` | `SUPERSEDED 2026-08-02: realised spend is $77.28 machine-ledgered, best estimate $133.38. …` | `$77.28 machine-ledgered` |
| `aso_ewsr1_partner_share_wilson_upper_87_8` | `67.2–87.8% — the Wilson 95% interval for 46/58 is 67.2308–87.7485% …` | `67.2–87.8%` |
| `commit_loop_gate13_446s_85_to_94_percent` | `gate 13 is 446.3 s over 1030 tests and 44% of a 130.7 s default loop (2026-09-02). …` | `446.3 s` ⚠ see R.4 |
| **hand-corrected (R.3)** | | |
| `card_rtx4090_755_36` | `RTX 4090 = 755.36 ns/day (median of 6 hosts); REFERENCE_NS_PER_H = 755.36/24 = 31.47` | `755.36` |
| `card_rtx4080_703_51` | `RTX 4080 = 703.51 ns/day (median of 4 hosts)` | `703.51` |
| `card_rtx3090_359_36` | `RTX 3090 = 359.36 ns/day (median of 3 hosts)` | `359.36` |
| `card_a100pcie_and_3090ti_first_pass_medians` | `A100 PCIe = 523.82 (provisional median of 2 hosts); RTX 3090 Ti = 481.87 (median of 3 hosts)` | `523.82` |
| `valb_rung_band_8_78_22_28` | `valB 4-leg replicate pair: plan $8.78, ceiling $22.28 (ternary_vast_launch.rung_band_usd(4))` | `8.78` |
| `valb_miss_magnitude_and_ratio` | `valB_mini at the landed n=3: mean -0.599 kcal/mol, abs error 1.478, ~34x the 0.045 statistical uncertainty` | `1.478` |
| `ladder_basis_0_004359` | `basis $0.004359/ns (congeneric_fanout.basis_usd_per_ns())` | `0.004359` |
| **the 40th (W28c's promoted entry)** | | |
| `rbfe_edge_tyk2_rate` | `~5–6 ref GPU-h ≈ ~$0.6–1.4 per RBFE edge` | `$0.6–1.4` |

Every one of the 39 passed rigor gate 2 (the match overlaps a transplanted numeral) and, with the single exception of `commit_loop_gate13_446s_85_to_94_percent`, rigor gate 1 (the guard does **not** already fire on unchanged `current`).

⚠ **`rbfe_edge_tyk2_rate` — I confirm W28c's promotion, and I sharpen why.** The pattern writes the retired quantity as a *range* (`\$0\.6[–-]1\.4`) where `current` writes a *single value* (`~$1.9`), so the frame screen cannot hit by construction — the arity of the quantity slot differs. Controls run: the unchanged `current` is NO MATCH; swapping only the GPU-h quantity (`~5–6 ref GPU-h ≈ ~$1.9 …`) is NO MATCH (alt 1 needs `5–6 GPU-h` adjacent, and `current` writes `ref` between); swapping the dollar quantity fires alt 2. **The screen's blind spot is arity, not wording** — a named, checkable failure mode rather than an anecdote.

### R.3 — The screen's real defect: eight fixtures were mangled by **bare-numeral frames**, and that is where its error lives `PRIMARY`

For an alternative that is a bare literal (`755\.36`, `703\.51`, `359\.36`, `8\.78|22\.28`, `1\.478`, `523\.82|481\.87`, `1070\.44|…`), the frame degenerates to `([0-9]+(?:\.[0-9]+)?)` — **"any number"** — so the screen's hit is vacuous and the automatic transplant lands on whatever number comes first in `current`. It replaced a **card model name**: `RTX 4090 = 804.06` became `RTX 755.36 = 804.06`; `A100 PCIe` became `A523.82 PCIe`; `valB 4-leg` became `valB 8.78-leg`; `landed n=3` became `landed n=1.478`.

**Those eight fixtures are inadmissible as written** — no writer would produce them, and a MATCH on them proves only that the number appears somewhere. Hand-correcting the swap to the genuine quantity slot (each fixture above) leaves seven at **MATCH**, and one with no quantity slot at all.

⛔ **This is the concrete reason to distrust an unaudited frame screen, and it is bigger than the 1-in-14 headline.** 8 of 40 (20%) of the screen's WOULD-MATCH calls rested on a vacuous frame. Seven happened to be right anyway; one was not. The screen's *verdicts* are 97.5% right; its *reasoning* is 80% right. A successor that reported the screen's fixtures as evidence would have published eight fixtures that are not admissible under the shared rule.

### R.4 — Two entries need a caveat attached to their MATCH `PRIMARY`

⛔ **`single_host_new_card_figures_2026_07_27` — reclassified WOULD-MATCH → UNTESTABLE.** Its `current` is `the median-of-N entries in vast_cost_model.MEASURED_NS_PER_DAY_84K` — a bare pointer to a constant, containing **no quantity slot**. No transplant fixture is constructible from the entry's own field. Searching the tree for an admissible external quotation of the retired construction, `grep -rn "1070\.44\|793\.79\|482\.34\|481\.78\|387\.78\|242\.20"` returns hits only in `research/modalities/vast-bench-sweep-results.json`, `vast-market-offers-raw.json`, `throughput-bench-provenance.json` and `vast_cost_model.py` comments — where those figures are **current per-host readings retained as provenance behind the medians**, not restatements of the retired claim. Using them as a fixture would test something else. **UNTESTABLE**, and the frame screen's hit on it was an artifact of the bare-numeral degeneracy in R.3.

⚠ **`commit_loop_gate13_446s_85_to_94_percent` — MATCH, but the transplant is uninformative.** Its `current` *retains the retired literals verbatim* ("The 446.3 s / 1247.8 s readings described the gate BEFORE its hot spot was removed"), so the guard already fires on the unchanged `current` and the swap adds nothing. This independently reproduces W28c's R.3 observation by a different route. The transplant verdict stands as MATCH but carries no extra information.

### R.5 — The stronger instrument neither predecessor ran: **58 of 81 guards fire on real committed target text today, 246 times, and every one is cleared** `PRIMARY`

While checking fixture admissibility I ran the real compiled patterns over the real 29 `targets[]` files through the real `lint_consistency.py` (`_read_lines` + `is_cleared`, loaded via `importlib`, read-only). This needs **no fixture at all** — the text is committed, so the fixture-rule problem disappears.

| | n |
|---|---|
| distinct `superseded[]` entries matching live target text | **58 / 81** |
| total live matches | **246** |
| matches **not** cleared by a supersession marker (would be `ERROR`) | **0** |

Top-firing files: `research/compute/pricing.md` (55), `research/manuscripts/program/degrader-paper-schedule.json` (44), `STRATEGY.md` (42), `systems/views/plan.md` (26), `research/compute/bid-strategy.md` (17).

Three consequences, in descending importance:

⛔ **33 of the 40 are proved live by committed text, with no fixture construction whatsoever.** For those, the transplant result is corroborated by a strictly stronger form of evidence. The 7 without a live match are `aso_ewsr1_partner_share_wilson_upper_87_8`, `card_a100pcie_and_3090ti_first_pass_medians`, `commit_loop_gate13_446s_85_to_94_percent`, `realised_spend_omitted_the_selcal_lane`, `single_host_new_card_figures_2026_07_27`, `ternary_lane_valb_cohort3_rates`, `valb_rung_band_8_78_22_28` — for those six (excluding the reclassified one) the transplant remains the only evidence.

⛔ **Three of W28c's 13 WOULD-NOT-MATCH entries fire on real committed text**: `buy_line_1_5x_multiple_expression`, `card_ratio_4090_over_4080_within_7pct`, and `xtt_pre_harmonized`. W28c's negatives are correct *as stated* — those guards do not catch the value written the way their own `current` writes it — but **they are not inert**, and reading the 13 as a dead-guard count would be wrong for at least these three. This is a correction available to the campaign that neither W28b nor W28c could have seen, because both tested fixtures rather than the tree.

⚠ **The whole 246-match cleared population is a standing measurement of `is_cleared`, not of the patterns.** Every superseded value that appears in a target today is escorted by a marker. That is the registry working as designed; it also means the guards' *only* live exercise path is through `is_cleared`, so a regression there would silently un-cover 58 guards at once. I did not test `is_cleared` beyond observing its verdicts.

### R.6 — The tree passes today; everything above is latent `PRIMARY`

```
$ python3 research/manuscripts/lint_consistency.py
lint_consistency: 0 ERROR across 29 target file(s)
LINT_EXIT=0
```

## Validation evidence

All `RUN`, `python3` stdlib only, scratch under `/tmp/claude-0/w28d/` (deleted), against `/home/user/Rare-cancers` at HEAD `408b676a` (unchanged start to end).

**Run 1 — `transplant_all.py`, exit 0.** Top-level alternation splitter, numeric-literal extraction, frame screen, mechanical transplant, run against the real compiled patterns. Verbatim head:
```
frame-screen WOULD-MATCH (transplant built): 39
MATCH   : 39
NO MATCH: 0
identical-fixture (no numeral actually changed): 0
other   : 42
```
Per-entry `MATCH alt<N> <id> changed=True matched=<...>` lines and the 42 `EXCLUDED` lines were printed in full; the excluded set contains all 13 of W28c's confirmed negatives by name plus `rbfe_edge_tyk2_rate`.

**Run 2 — `rigor.py`, exit 0.** The two rigor gates over all 39. Verbatim tail:
```
FLAGGED: 1
  ('commit_loop_gate13_446s_85_to_94_percent', 'MATCH', ["ALSO-MATCHES-UNCHANGED-CURRENT('446.3 s')"])
```
Zero entries flagged `MATCH-DOES-NOT-TOUCH-TRANSPLANT`; zero multiline fixtures.

**Run 3 — `fix.py`, exit 0.** The seven hand-corrected transplants, each with a control on the unchanged `current`. Verbatim:
```
MATCH     card_rtx4090_755_36        matched='755.36'   pre_on_unchanged_current=False
MATCH     card_rtx4080_703_51        matched='703.51'   pre_on_unchanged_current=False
MATCH     card_rtx3090_359_36        matched='359.36'   pre_on_unchanged_current=False
MATCH     card_a100pcie_and_3090ti_first_pass_medians matched='523.82' pre_on_unchanged_current=False
MATCH     valb_rung_band_8_78_22_28  matched='8.78'     pre_on_unchanged_current=False
MATCH     valb_miss_magnitude_and_ratio matched='1.478' pre_on_unchanged_current=False
MATCH     ladder_basis_0_004359      matched='0.004359' pre_on_unchanged_current=False
```

**Run 4 — `rbfe.py`, exit 0.** Four fixtures with controls:
```
A quantity-slot transplant, both quantities   MATCH     '$0.6–1.4'  || ~5–6 ref GPU-h ≈ ~$0.6–1.4 per RBFE edge
B dollar quantity only                        MATCH     '$0.6–1.4'  || ~13.7 ref GPU-h ≈ ~$0.6–1.4 per RBFE edge
C GPU-h quantity only                         NO MATCH  None        || ~5–6 ref GPU-h ≈ ~$1.9 per RBFE edge
D unchanged current (control)                 NO MATCH  None        || ~13.7 ref GPU-h ≈ ~$1.9 per RBFE edge
```

**Run 5 — `live.py`, exit 0.** Real `lint_consistency.py` loaded via `importlib`, real `targets[]`, real `is_cleared`. 246 match lines; `grep -c "cleared=True"` → **246**; `grep "cleared=False"` → **empty**; 58 distinct entry ids.

**Run 6 — the real linter, unmodified:** `lint_consistency: 0 ERROR across 29 target file(s)`, `LINT_EXIT=0`.

**Run 7 — state verification.** `git diff --stat 408b676..HEAD -- research/manuscripts/pinned-figures.json research/manuscripts/lint_consistency.py` → empty; md5sums recorded; `git status --porcelain` empty at both ends; scratch deletion confirmed by `ls` returning `No such file or directory`.

**`PROPOSED (NOT RUN)`** — everything in "Next concrete action". No repair, patch, gate, test, registry edit, field addition, pattern change or `targets[]` change was authored, proposed as code, or executed. `scripts/preflight.sh` and `PREFLIGHT_FULL` not run.

## Limitations

- **A MATCH means the guard catches the retired value written the way the entry's own `current` writes that quantity. It is not proof the guard catches the original retired line.** The clone is shallow and pre-window wording is unrecoverable, so no verdict here grades any guard "born correct" or "born broken" against the text it was actually written for. That is an unrecovered source, not an absence.
- **The 39 MATCH verdicts are a *lower* bound on brittleness, not an upper bound.** A transplant tests one sentence shape — the registry's own. A guard that matches its own `current` shape can still miss the same value written in a different sentence elsewhere; W28c's 13 negatives are exactly that class, and R.5 shows three of them nonetheless fire on live text.
- **I re-derived the screen rather than importing W28c's list.** Agreement on 40 of 40 calls (39 + the known `rbfe` correction) is strong but not a proof that both implementations share no common blind spot; both are frame-based and both would miss an arity mismatch without the transplant step.
- **R.5's 58/81 is a count of entries firing on the 29 declared targets only.** Files outside `targets[]` were not scanned; a guard silent there is UNKNOWN, not dead. `research/compute/pricing.md` is a target and carries several retired literals under a `⚠ SUPERSEDED` row, which is why they clear.
- I tested **regex liveness and clearance verdicts**. I did not test `is_cleared`'s window mechanics, and I did not test whether any firing guard would be *spuriously* cleared.
- **Untouched and left with the file owner**, exactly as W28b and W28c left them: the `aso_thermo_cross_margin_discordance` filing question, the `targets[]` membership question, and the `$126.17` current-vs-retired disagreement. I re-litigated none of them.
- Nothing here is a scientific or clinical claim. It concerns a lint registry. There is no wet lab and no patient-facing consequence.

## Stop condition

Set up front: **stop when all 40 of W28c's WOULD-MATCH entries carry an individual transplant verdict — MATCH, NO MATCH, or reclassified UNTESTABLE — each with its fixture quoted and each run against the real compiled pattern, and a measured screen error rate is stated with a real `lint_consistency.py` exit code recorded.**

**MET.** 40 verdicts (R.2): 39 MATCH, 1 UNTESTABLE, 0 refuted; screen error rate 1/40 = 2.5%, direction characterised (R.2, R.3). Fixtures quoted for all 40. Exit code in R.6. Stopped there; R.5 arrived inside the same work as a by-product of checking fixture admissibility and is reported, not expanded on.

## Tool-call and wall-clock count actually used

**11 tool calls** (all `Bash`), against a ~40 target. **Wall clock 04:35:15Z → 04:39:56Z = 4 min 41 s**, against a ~40 min target. Under both: the registry is one `json` load and the decisive evidence was four scripts and two greps. Early return is the success case per the brief.

## Next concrete action

**For the campaign, one bounded correction to the standing W28c result, requiring no repository write and no owner judgement:** record that the frame screen's WOULD-MATCH count is **39, not 40** (`single_host_new_card_figures_2026_07_27` has no admissible fixture and moves to UNTESTABLE, making the registry-wide split **39 / 13 / 29**), and that the instrument's measured error over all 81 entries is **one false negative and zero false positives**, with the failure mode named — **bare-numeral alternatives produce vacuous frames (8 of 40 calls), and quantity-arity mismatches produce false negatives (1 of 81)**. That closes the successor task W28c opened, with a measured rate rather than an anecdote.

Three things that should travel with it but are **not** part of that action:

1. **R.5 is the better instrument and it is cheap.** Running the compiled patterns over the real 29 targets through the real `is_cleared` needs no fixture, no reconstruction, and no interpretive rule: **58 of 81 guards demonstrably fire on committed text, 246 times, all cleared.** Any future liveness question in this lane should start there and use transplants only for the ~23 entries the tree cannot exercise.
2. **Three of W28c's 13 WOULD-NOT-MATCH entries are not inert** — `buy_line_1_5x_multiple_expression`, `card_ratio_4090_over_4080_within_7pct`, `xtt_pre_harmonized` all match live target text. The 13 is a count of *phrasing fragility against the registry's own `current`*, and must not be reported as a dead-guard count.
3. **The registry's guards are exercised today only through `is_cleared`** (0 of 246 live matches are uncleared). That concentrates the risk: a regression in clearance logic would flip 58 guards at once. Testing `is_cleared` is a distinct lane with its own `_WINDOW_CHARS` history, and I did not open it.

**Successor for this lane:** none is needed for the WOULD-MATCH set — it is now individually tested and corroborated. The nearest genuinely open question is whether the ~23 `superseded[]` entries with **no** live match in any target are silent because their value is truly gone or because the guard cannot reach it; R.5 gives the denominator for that question for the first time.
