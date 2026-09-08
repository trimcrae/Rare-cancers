<!-- collected 2026-09-08T03:38:44Z by campaign coordinator; agent id a0d92fa75bd99403e; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a0d92fa75bd99403e.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

## Worker

**W28b**, lane: superseded-guard liveness (named successor to W28), OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model — `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the served model from the transcript.

**Write isolation honoured.** Nothing written under `/home/user/Rare-cancers`; no git write operation; all execution under `/tmp/claude-0/w28b/`, which was deleted before returning (`exists=no`). `scripts/preflight.sh` not run. No network, no paid API, no GPU spend. No guard written, no pattern fixed, no file added to any target list.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:31:27 UTC 2026` | `Tue Sep  8 03:35:44 UTC 2026` |
| `git rev-parse HEAD` | `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1` | `1c9d827870599576c0c027a9134363d59456fd04` |
| `git status --porcelain` | empty | empty |

HEAD moved under me twice (the parent collector is committing campaign reports); the tree stayed clean at both reads and neither commit touched `pinned-figures.json` or `lint_consistency.py`, both of which I read at HEAD. Note the checkout is **not** the frozen `92abbcb` named in COMMON-BRIEF §1.

Literal `env` grep output (start; end identical, both pasted from the same command form, secrets redacted by the prescribed `sed`) — reproduced in the Validation evidence section below.

## Question

For each of the six `superseded[]` guards W28's addendum found matching **zero times across all 7,741 tracked files**: does the guard still match the retired value **in the form the registry entry itself says that value took**? A guard that matches its own fixture is working and merely has nothing left to catch; a guard that does not is inert and would not fire if the value came back. Zero hits alone cannot tell those apart, and nothing in the repository distinguishes them.

Secondary: resolve the near-miss W28 flagged but declined to assert — whether `vaccine_e7_coverage_stated_without_a_panel` was meant to catch `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md:246`.

This is open because W28 named it explicitly as unresolved ("Nothing in the repository tests a guard's ability to still catch its own target") and handed the fixture question forward without running it.

## Prior-work check

Read in full: `CLAUDE.md`, `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W28-superseded-marker-audit.md` including its addendum, and `W09f-publications-false-absence-audit.md` R.3 (a `publications.json` prose-scope finding about `PUB-LOCOREGIONAL`; unrelated to guard liveness, so nothing to replay).

Commands run:

- `grep -n -i "addendum\|inert\|superseded\[\]\|zero" W28-superseded-marker-audit.md` — confirmed the six-at-zero addendum at `:330-347` and its explicit hand-off.
- `grep -rn "15:01 alone" --include=*.md --include=*.json .` (excluding `.git`) — 14 live occurrences across 9 files.
- `grep -rn "must_not_appear_in" --include=*.py .` — **no hits.**
- `git ls-files | grep -i test_lint_consistency` → `research/modalities/tests/test_lint_consistency.py` (single test file; not under `tests/`).
- `git log --all --oneline -S'<retired string>'` for six retired strings; `git rev-list --count HEAD` = 346 and `.git/shallow` present.

Nothing in `CLOSED-WORK.md` covers registry-guard liveness. I am not replaying W28's Parts 1-4; I take the six-at-zero result as W28's premise and test the distinct question it left open.

## Method / inputs

Files read at HEAD:

- `/home/user/Rare-cancers/research/manuscripts/pinned-figures.json` — `_README`, `_marker_note`, `targets` (29), all 81 `superseded[]` entries; the six target entries dumped in full.
- `/home/user/Rare-cancers/research/manuscripts/lint_consistency.py` — `check_superseded`, `is_cleared`, `lint`, `main`.
- `/home/user/Rare-cancers/research/modalities/tests/test_lint_consistency.py`.
- `/home/user/Rare-cancers/STRATEGY.md:128` (Appendix A row 58).
- `/home/user/Rare-cancers/research/manuscripts/neoantigen/emc-vaccine-development-path.md` lines 74, 327, 393, 1541.
- `/home/user/Rare-cancers/research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md` lines 236-252.
- `/home/user/Rare-cancers/research/manuscripts/neoantigen/hla-coverage-emc.md:31`.

Tools: `python3 3.11.15` stdlib `re` and `json` only, no third-party deps; `git` (shallow clone, 346 commits); `grep`. Two scratch scripts under `/tmp/claude-0/w28b/`, both since deleted; their full source is quoted below so the runs are reproducible.

**Fixture rule I bound myself to.** A fixture is admissible only if its wording comes from committed text — either the entry's own `current` field modelling the sentence shape, or a verbatim quotation of the retired construction elsewhere in the tree. I did **not** unescape a pattern into a string and call the resulting match a pass; that is circular and proves only that the regex parses. Where neither source exists, the guard is reported **UNTESTABLE**, not "working".

## Result

### R.1 — The split: 3 working, 1 partial, 2 untestable from the registry alone `PRIMARY`

| # | guard | fixture source | verdict | grade |
|---|---|---|---|---|
| 1 | `ternary_lane_valb_cohort3_rates` | entry's own `current` models the sentence | **MATCHES its fixture — WORKING** | PRIMARY |
| 2 | `realised_spend_before_orphan_leak` | none exists | **UNTESTABLE** | UNKNOWN |
| 3 | `realised_spend_before_retro_orphan_leak` | none in entry; external quote exists | **UNTESTABLE from the registry**; fails the tree's own retained restatement | UNKNOWN / PRIMARY |
| 4 | `realised_spend_omitted_the_selcal_lane` | entry's own `current` models the sentence | **PARTIAL — 1 of 3 alternatives fires** | PRIMARY |
| 5 | `aso_thermo_cross_margin_discordance` | entry's own `note` | **MATCHES — but it is not a superseded-value guard at all** | PRIMARY |
| 6 | `vaccine_e7_coverage_stated_without_a_panel` | entry does not quote the retired wording | **UNTESTABLE on alt 1; alt 2 WORKING but never met** | UNKNOWN / PRIMARY |

Guard by guard, with the exact fixture and its provenance. **Every fixture below is my reconstruction of the retired text unless its source line is cited; none is the original.**

---

**1 · `ternary_lane_valb_cohort3_rates` — WORKING** `PRIMARY`

Pattern `1\.528\s*[x×]|1\.574\s*[x×]|\$0\.005214/ns|\$0\.005369/ns`. The entry's `current` states the replacement in a definite form — *"valB_mini cohort 4, rented 4:51 PM ET: 1.500x / 1.500x / 1.859x / 1.649x basis"* — so the retired cohort-3 sentence took the same shape. Two fixtures:

- `valB_mini cohort 3, rented 4:00 PM ET: 1.528x / 1.574x / 1.859x / 1.649x basis` → **MATCH** (`'1.528x'`); alts 1 and 2 both fire independently.
- `cohort 3 drift $0.005214/ns and $0.005369/ns against basis` → **MATCH** (`'$0.005214/ns'`); alts 3 and 4 both fire.

All four alternatives are live. This guard would catch its target if it returned. Its zero is the success case.

---

**2 · `realised_spend_before_orphan_leak` — UNTESTABLE** `UNKNOWN`

Pattern `\+\$2\.31 attested|best estimate is \*\*\$79\.59\*\*`. The entry's `current` and `retired_by` describe the *mechanism* of the leak in detail and never quote the retired sentence. Searching the tree, `+$2.31 attested` returns nothing and `79.59` returns exactly one hit — `research/modalities/nr4a3-orientation-basins.json:5503`, the float `79.598` in an unrelated numeric array. `git log -S` finds neither string, but the clone is **shallow** (`.git/shallow` present, `git rev-list --count HEAD` = 346), so history is not a usable witness and its silence proves nothing.

I therefore cannot construct a fixture without inventing the retired wording. **UNTESTABLE from the registry alone.** I decline to unescape the pattern and call it a pass.

---

**3 · `realised_spend_before_retro_orphan_leak` — UNTESTABLE from the registry; FAILS the repository's own retained restatement** `UNKNOWN` / `PRIMARY`

Pattern `\+\$22\.31 attested|best estimate is \*\*\$99\.59\*\*`. The entry itself quotes nothing, so on the task's own rule it is **UNTESTABLE from the registry alone**.

But unlike #2, a real committed witness exists. `STRATEGY.md:128`, Appendix A row 58, restates the retired pair in the "what was wrong" column:

> Realised spend **attested-only $22.31** and **best estimate $99.59** (this file's Spend summary, 2026-07-31 morning)

Tested as a fixture: **NO MATCH**, and both alternatives fail separately.
- `\+\$22\.31 attested` needs `+$22.31 attested`; the retained text reads `attested-only $22.31`.
- `best estimate is \*\*\$99\.59\*\*` needs the word `is` and asterisks hugging the figure; the retained text reads `**best estimate $99.59**`, with the emphasis around the whole phrase and no `is`.

⚠ **What this does and does not establish.** Row 58 is the repository's own restatement of the retired figure, not necessarily the wording of the 2026-07-31 Spend summary the pattern was written against — that original line is not recoverable from this shallow checkout. So this is *not* proof the guard was born broken. It is proof of something narrower and still useful: **the only surviving text in this repository that states the retired pair does not trip the guard**, and the two ways it fails (a dropped `is`, emphasis moved by one word) are exactly the reformat-fragility class W28 named. A writer reintroducing the figure from row 58's wording would not be caught.

---

**4 · `realised_spend_omitted_the_selcal_lane` — PARTIAL, 1 of 3 alternatives fires** `PRIMARY`

Pattern `\$77\.28 machine-ledgered|best estimate is \*\*\$126\.17\*\*|realised spend \$77\.28`. This entry *does* model the sentence: `current` reads *"SUPERSEDED 2026-08-02: realised spend is $84.49 machine-ledgered, best estimate $133.38. **The old pair** was not merely out of date…"*. Substituting the old pair into the form the entry itself writes gives the fixture:

`realised spend is $77.28 machine-ledgered, best estimate $126.17`

**MATCH**, via alternative 1 only:

| alternative | fires? | why |
|---|---|---|
| `\$77\.28 machine-ledgered` | **yes** | matches |
| `best estimate is \*\*\$126\.17\*\*` | **no** | fixture has no `is` and no `**` |
| `realised spend \$77\.28` | **no** | fixture reads `realised spend **is** $77.28` |

So the guard is **live but half-dead**: it catches the machine-ledgered figure and misses the best-estimate figure in the very sentence shape its own `current` field writes. The identical `best estimate is \*\*\$…\*\*` construction fails in #2, #3 and #4 — one author's habit replicated across three guards, and the single most likely thing to fix.

⛔ **Separate observation, and the file owner's call, not mine.** Entry #4 declares `$126.17` retired as of 2026-08-02 in favour of `$133.38`. Entries #2 and #3 both state, in their `current` field, *"Attested-only is $48.89 and the best estimate $126.17"*. Those are prose fields the linter does not check, so nothing fires and this is not a lint failure — but the registry currently carries `$126.17` as both the current best estimate (two entries) and a retired one (a third). `STRATEGY.md:128` also states `$126.17` as current. Which is right is the owner's judgement; I only record the disagreement.

---

**5 · `aso_thermo_cross_margin_discordance` — matches its fixture, but it is not a superseded-value guard** `PRIMARY`

Pattern `composition reverses the\s+order in\s+([0-9]{1,2}\.[0-9])\s*%\s*of cross-margin`. Fixture from the entry's own `note` (*"19.9% — 2,298 of 11,552 cross-margin design pairs"*):

- `composition reverses the order in 19.9% of cross-margin design pairs` → **MATCH**.
- **Control fixture**, same sentence with a different number: `composition reverses the order in 41.7% of cross-margin design pairs` → **also MATCH**.

⛔ **The control is the finding.** The pattern carries a capture group `([0-9]{1,2}\.[0-9])` where every other `superseded[]` entry hard-codes the retired literal. It matches *any* one-decimal percentage in that sentence — including the current, correct 19.9%. `check_superseded` never reads the capture group; it only reports `m.group(0)` as "stated without marking it superseded". So as filed, this guard would flag the paper for stating its own current value. This entry's shape (`artifact` + `note`, no `current`, no `retired_by`) is that of an `artifact_figures[]` entry, not a `superseded[]` one. **Whether it is misfiled is the registry owner's judgement; I am not moving it.**

---

**6 · `vaccine_e7_coverage_stated_without_a_panel` — alt 1 UNTESTABLE, alt 2 WORKING but never met** `UNKNOWN` / `PRIMARY`

Pattern `predicted to be presented on HLA-B\\?\*15:01 alone|\| B\\?\*15:01 alone \|`.

*Correcting W28 on the doubled escape.* W28 listed `HLA-B\\?\*15:01` among the three brittle constructions. It is not brittle — it is the opposite. In regex, `\\?` is an **optional literal backslash**, so the alternative matches both `HLA-B*15:01` and the markdown-escaped `HLA-B\*15:01`. That is a deliberate widening for markdown source, and it works. The brittleness in this entry lies elsewhere.

Fixtures, all six drawn from real committed lines (per-alternative results):

| fixture | source | alt 1 | alt 2 |
|---|---|---|---|
| `\| "presented on HLA-B\*15:01 alone", stated without naming a panel \|` | `emc-vaccine-development-path.md:1541`, verbatim | no | no |
| same, unescaped `HLA-B*15:01` | derived from the above | no | no |
| `is now presented on **B\*15:01 alone** —` | `fusion-junction-neoantigen-paper.md:245` | no | no |
| `covers 8.5% on ten alleles, presented on HLA-B\*15:01 alone, and 12.3% on` | `emc-vaccine-development-path.md:74` | no | no |
| `\| e7::e3 public junction, alleles \| A\*11:01 + B\*08:01 \| **B\*15:01 alone** \|` | `hla-coverage-emc.md:31` | no | no |
| `\| B*15:01 alone \|` and `\| B\*15:01 alone \|` | plain and escaped bare table cell | no | **yes** |

**Alternative 1 is UNTESTABLE, and there is positive evidence against calling it broken.** The entry never quotes the retired wording; `retired_by` only says *"The bare form was in the Abstract, Section 2.3, B1 and Appendix A."* The one verbatim quotation in the tree (`:1541`) records the retired construction as *"presented on HLA-B\*15:01 alone", stated without naming a panel* — no `predicted to be`. It is tempting to conclude the prefix is spurious over-tightening. **It is not, and here is why:** that shorter phrase is a literal substring of text the entry's own `current` and `id_note` declare **true** — `:74`, `:327` and `:393` all say the junction is presented on HLA-B\*15:01 alone *and name the ten-allele screen*. A guard on the bare phrase would flag three true sentences, which the registry `_README` calls the founding failure mode ("a linter that flags true statements gets ignored"). The `predicted to be` prefix is therefore load-bearing disambiguation, and whether it reproduces the retired wording is **UNKNOWN**. I will not grade it broken on evidence that is equally consistent with it being right.

**Alternative 2 is WORKING but structurally unreachable.** It matches `| B*15:01 alone |` and the escaped variant — so the regex is live. But the actual table cell it was presumably aimed at, `hla-coverage-emc.md:31`, reads `| **B\*15:01 alone** |` with bold, and does not match. W28's "exact table-cell shape" charge is **confirmed**: this alternative fires only on an unemphasised cell, and the repository's tables emphasise. Note also `hla-coverage-emc.md` is not in `targets[]`, so the alternative would not run there regardless.

---

### R.2 — Two of the six would CRASH the linter rather than report, and it is because they have never fired `PRIMARY`

This is a new defect, not in W28. `check_superseded` (`lint_consistency.py:610-612`) formats every finding as:

```python
f"current: {entry['current']} | retired by: {entry['retired_by']}"
```

Direct `dict` subscripts on both keys. Across all 81 `superseded[]` entries:

- missing `current`: **1** — `aso_thermo_cross_margin_discordance`
- missing `retired_by`: **2** — `realised_spend_omitted_the_selcal_lane`, `aso_thermo_cross_margin_discordance`

⛔ **Both schema-incomplete entries are inside the six dead guards.** 2 of the 6 dead guards are malformed against 0 of the other 75. That is not coincidence — a guard that has never matched has never executed that f-string, so the `KeyError` was never surfaced. Never firing is exactly what hid the defect.

I ran this against the live linter, not by inspection. Feeding each guard a one-line fixture repository through `lc.check_superseded(sub, repo=…, targets=[…])`:

```
realised_spend_omitted_the_selcal_lane: *** KeyError: 'retired_by' *** (linter CRASHES when this guard fires)
aso_thermo_cross_margin_discordance:    *** KeyError: 'current'    *** (linter CRASHES when this guard fires)
ternary_lane_valb_cohort3_rates:        OK, 1 finding(s) -> S-ternary_lane_valb_cohort3_rates
```

The control confirms the harness reports normally for a well-formed entry. So if either retired value ever returned to a target file, CI would fail with an unhandled `KeyError` and no diagnostic naming the value — a worse outcome than the silent pass, because the traceback points at the linter rather than at the manuscript.

### R.3 — The repository already holds the principle W28 asked for; it is applied to `subset_checks` and not to `superseded[]` `PRIMARY`

`research/modalities/tests/test_lint_consistency.py:317`:

```python
def test_subset_fails_loudly_if_a_pattern_matches_nothing(tmp_path):
    """A reformat that breaks the regex must fail, not silently pass forever."""
    …
    assert any(f["rule"] == "X-pattern-found-nothing" for f in out)
```

`check_subsets` emits `X-pattern-found-nothing`. `check_superseded` has no equivalent — for it, matching nothing is indistinguishable from success, which is the correct default for a retired value and precisely why the liveness question needs a different mechanism. The registry's own test file also enforces a pattern-quality policy (`test_registry_patterns_are_not_bare_numbers`, line 350) but nothing checks entry schema completeness. So the gap is narrow and already articulated in this repository's own words.

### R.4 — The near-miss, resolved as far as the entry can resolve it `PRIMARY` / `UNKNOWN`

**Was `vaccine_e7_coverage_stated_without_a_panel` meant to catch `fusion-junction-neoantigen-paper.md:246`?**

Reading the entry's own text, three fields bear on it, and they point the same way:

- `must_not_appear_in: ["research/manuscripts/neoantigen/emc-vaccine-development-path.md"]` — **one file, and it is not that one.**
- `retired_by` locates the retired form only *within* that document: *"The bare form was in the Abstract, Section 2.3, B1 and Appendix A."*
- `current` points the reader to *"emc-vaccine-development-path.md Section 2.3 and its Appendix B"*.

**Answer: the guard as written is scoped to `emc-vaccine-development-path.md`, and on the entry's own text was not aimed at `fusion-junction-neoantigen-paper.md`.** Whether the author *intended* the underlying prohibition to generalise to the other paper is **UNKNOWN** — the entry does not say, and I will not read intent into a scope field.

Two things the owner should have alongside that answer:

⛔ **`must_not_appear_in` is dead metadata.** `grep -rn "must_not_appear_in" --include=*.py .` returns **no hits**. No code reads the field. It is the only `superseded[]` entry carrying it. So the scope it declares is documentary; the actual scope is `targets[]`, which excludes both files in question.

⚠ **The near-miss line does exhibit the defect shape the entry describes, on the entry's own criterion.** The entry's test is whether the claim is *"stated without naming a panel"*. At `fusion-junction-neoantigen-paper.md:245-246` the paper states the junction *"is now presented on **B\*15:01 alone**… and covers **≈8.5% of patients**"*. `grep -n "ten-allele\|ten alleles\|34-allele\|34 alleles"` over that entire file returns **nothing** — the paper never names a panel anywhere, and 8.5% is the ten-allele figure. So the shape matches the entry's criterion even though the regex does not match the text. Whether that is a live defect in that manuscript, and whether the file belongs in `targets[]`, is the paper owner's decision — the same decision W28's successor action already puts in front of them. I assert only the grep result and the entry's own wording.

## Validation evidence

All runs `RUN`, on `python 3.11.15`, in `/tmp/claude-0/w28b/` (since deleted), against `/home/user/Rare-cancers` at HEAD.

**Run 1 — `python3 /tmp/claude-0/w28b/fixture_test.py`, exit 0.** Twelve fixtures across the six guards; per-guard results are quoted verbatim in R.1. Full source, reproducible:

```python
import json, re, sys
reg=json.load(open("/home/user/Rare-cancers/research/manuscripts/pinned-figures.json"))
by={e["id"]:e for e in reg["superseded"]}
for eid, tag, provenance, fixture in F:      # F as tabulated in R.1
    pat = by[eid]["pattern"]
    if fixture is None: print(f"[{eid}/{tag}] UNTESTABLE: {provenance}"); continue
    m = re.compile(pat).search(fixture)
    print(f"[{eid}/{tag}] {'MATCH' if m else 'NO MATCH'}  matched={m.group(0)!r} if m")
```

⚠ **Self-correction on my own harness.** Run 1's per-alternative breakdown split each pattern on `"|"`, which is wrong for the vaccine guard because its literal `\|` contains a pipe; that produced three spurious `REGEX-ERR bad escape` lines. Those errors are **my splitting artifact, not registry defects** — the full patterns all compile (W28's 0/81 bad-regex count stands). Run 2 re-tested that guard with the alternatives split by hand; R.1's table #6 uses Run 2.

**Run 2 — `python3 /tmp/claude-0/w28b/verify2.py`, exit 0.** Part A, corrected per-alternative test, verbatim:

```
  1541_retained_quote      alt1=False  alt2=False
  1541_unescaped           alt1=False  alt2=False
  246_near_miss            alt1=False  alt2=False
  74_true_current          alt1=False  alt2=False
  hla_cov_table_cell       alt1=False  alt2=False
  plain_table_cell         alt1=False  alt2=True
  md_escaped_table_cell    alt1=False  alt2=True
  hypothetical_retired     alt1=True   alt2=False
```

(`hypothetical_retired` is my own construction containing `predicted to be`; it shows alternative 1 compiles and fires, nothing about the original wording.)

Part B loaded the real `lint_consistency.py` via `importlib` and called `check_superseded` with a one-entry registry and a one-line fixture repo; output quoted verbatim in R.2.

**Run 3 — schema scan over all 81 entries, exit 0:**
```
total superseded: 81
missing current   (1): ['aso_thermo_cross_margin_discordance']
missing retired_by(2): ['realised_spend_omitted_the_selcal_lane', 'aso_thermo_cross_margin_discordance']
```

**Run 4 — the real linter, unmodified, on the real repo:**
```
$ python3 research/manuscripts/lint_consistency.py
lint_consistency: 0 ERROR across 29 target file(s)
LINT_EXIT=0
```
The tree passes today. Every defect in R.1-R.3 is latent: it costs nothing until a retired value returns.

**Run 5 — history search.** `git log --all --oneline -S` for six retired strings; the only hits were commits containing W28's own report quoting the patterns. `.git/shallow` present, `git rev-list --count HEAD` = 346. History is **not** an admissible witness here and its silence is UNKNOWN, not absence.

**`PROPOSED (NOT RUN)`** — everything in "Next concrete action": no repair, no test, no registry edit, no `targets[]` change was written or executed.

**Literal `env` output** (start and end identical; command `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`) — abridged to the model-relevant lines, full output in the transcript:
```
AI_AGENT=claude-code_2-1-263_agent
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDECODE=1
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_EFFORT=medium
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
```
No variable names a served model.

## Limitations

- **Every fixture is a reconstruction.** Only two are quotations of committed text (`STRATEGY.md:128`; `emc-vaccine-development-path.md:1541`), and both are the repository's *retained restatement* of a retired sentence, not the sentence. The rest are built from the shape the entry's own `current` field writes. A "WORKING" verdict means the guard catches the value **in the form the registry models**, not that it catches the original line.
- **A NO MATCH is not proof the guard was born broken.** Guards 3 and 6 could have been written correctly against original text this shallow checkout cannot show me. I graded them UNTESTABLE and reported the failing fixture separately rather than collapsing the two.
- The clone is shallow (346 commits), so `git log -S` cannot recover pre-window wording. That is an unrecovered source, not an absence.
- I tested regex liveness only. I did **not** test whether `is_cleared` would spuriously clear a firing guard, which is a separate mechanism with its own `_WINDOW_CHARS` history and its own tests.
- The `$126.17` current/retired disagreement (R.1 #4), whether the `aso_thermo` entry is misfiled (R.1 #5), and whether `fusion-junction-neoantigen-paper.md` belongs in `targets[]` (R.4) are all **the file owner's judgements**. I left every one of them.
- Nothing here is a scientific or clinical claim. It concerns a lint registry. There is no wet lab and no patient-facing consequence.
- HEAD moved twice mid-run (parent collector commits). Neither commit touched the two files I analysed, but a strict re-run should pin a single revision.

## Stop condition

Set up front: **stop when all six guards have a fixture verdict — WORKING, PARTIAL, BROKEN or UNTESTABLE, each with its fixture and provenance stated — and the `vaccine_e7…` near-miss is answered from the entry's own text or recorded UNKNOWN.**

**MET.** Six verdicts delivered (R.1); the near-miss answered from `must_not_appear_in`, `retired_by` and `current`, with the residual intent question recorded UNKNOWN (R.4). Two findings beyond the brief arrived inside the same work and are reported rather than expanded on: the `KeyError` crash pair (R.2) and the `X-pattern-found-nothing` precedent (R.3). I stopped there and did not open the registry-wide schema audit those suggest.

## Tool-call and wall-clock count actually used

**14 tool calls** (12 `Bash`, 2 `Read`), against a ~40 target. **Wall clock 03:31:27Z → 03:35:44Z = 4 min 17 s**, against a ~40 min target. Under both because the six entries were readable in one `json` dump and the decisive evidence was three greps and two scripts.

## Next concrete action

**For the owner of `research/manuscripts/pinned-figures.json`, one bounded change with one verification command:** add `retired_by` to `realised_spend_omitted_the_selcal_lane` and `current` + `retired_by` to `aso_thermo_cross_margin_discordance` — or move the latter to `artifact_figures[]`, where its `artifact`/`note` shape and its value-agnostic capture group say it belongs — then re-run `python3 research/manuscripts/lint_consistency.py`. This closes a confirmed unhandled-`KeyError` crash (R.2, reproduced live against the real linter) that fires the moment either retired value returns, it is two of 81 entries, and it needs no judgement about any manuscript's prose.

Two things that should travel with it but are **not** part of that action, because each is a judgement I left with its owner: the `best estimate is \*\*\$…\*\*` construction fails in three separate guards (R.1 #2/#3/#4) and is the single highest-yield pattern repair; and `$126.17` is currently both a current and a retired figure inside the same registry (R.1 #4).
